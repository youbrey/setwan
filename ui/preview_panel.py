"""
ui/preview_panel.py
=====================
Mixin untuk PANEL LIVE PREVIEW (kanan-bawah / kolom ketiga): merender
template terpilih dengan context saat ini menjadi gambar, di thread
terpisah supaya tidak membekukan UI.

Catatan: modul ini murni infrastruktur preview. Jika
docx2pdf/PyMuPDF/LibreOffice tidak terpasang, panel ini akan
menampilkan pesan "preview tidak tersedia" tanpa membuat aplikasi
crash.
"""

import os
import shutil
import subprocess
import tempfile
import threading
import time

import customtkinter as ctk

from optional_deps import HAS_FITZ, HAS_DOCX2PDF, fitz, Image, convert_to_pdf_word
from config import PREVIEW_TEMPLATES


class PreviewPanelMixin:
    def setup_preview_panel(self):
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(2, weight=1)

        lbl_title = ctk.CTkLabel(self.preview_frame, text="👁 Live Preview", font=("Arial", 13, "bold"))
        lbl_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.combo_preview_template = ctk.CTkComboBox(
            self.preview_frame, values=[t[0] for t in PREVIEW_TEMPLATES],
            command=lambda choice: self.schedule_preview_refresh(immediate=True))
        self.combo_preview_template.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")

        self.lbl_preview_status = ctk.CTkLabel(self.preview_frame, text="", font=("Arial", 10), text_color="gray")
        self.lbl_preview_status.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="w")

        self.preview_scroll = ctk.CTkScrollableFrame(self.preview_frame, label_text="")
        self.preview_scroll.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.preview_page_labels = []
        self._preview_placeholder = ctk.CTkLabel(self.preview_scroll, text="(Preview akan tampil di sini)")
        self._preview_placeholder.pack(pady=20)

        self._preview_after_id = None
        self._preview_lock = threading.Lock()
        self._preview_generation = 0

        if not (HAS_FITZ and (HAS_DOCX2PDF or shutil.which("soffice"))):
            self._set_preview_status("Live preview tidak aktif (docx2pdf/PyMuPDF/LibreOffice belum terpasang)")

    # ------------------------------------------------------------------
    # PENJADWALAN REFRESH (debounce)
    # ------------------------------------------------------------------
    def schedule_preview_refresh(self, immediate=False):
        if not (HAS_FITZ and (HAS_DOCX2PDF or shutil.which("soffice"))):
            return
        if self._preview_after_id:
            self.after_cancel(self._preview_after_id)
        delay = 50 if immediate else 700
        self._preview_after_id = self.after(delay, self._launch_preview_render)

    def _set_preview_status(self, text):
        try:
            self.lbl_preview_status.configure(text=text)
        except Exception:
            pass

    def _launch_preview_render(self):
        self._preview_generation += 1
        gen = self._preview_generation
        self._set_preview_status("Merender preview...")
        thread = threading.Thread(target=self._preview_worker, args=(gen,), daemon=True)
        thread.start()

    # ------------------------------------------------------------------
    # WORKER (THREAD TERPISAH)
    # ------------------------------------------------------------------
    def _preview_worker(self, gen):
        try:
            label, template_code, mode = next(
                t for t in PREVIEW_TEMPLATES if t[0] == self.combo_preview_template.get()
            )
        except StopIteration:
            return

        try:
            if self.current_view != "perjalanan_dinas":
                form_data = self.build_undangan_paripurna_form_data() if hasattr(self, "undangan_inputs") else {}
                from letters.undangan import render_preview_context, find_template_undangan_paripurna
                render_ctx = render_preview_context(form_data)
                template_path = find_template_undangan_paripurna()
            else:
                ctx = self.build_context()
                render_ctx = ctx
                template_path = None
                if template_code not in ("__surat_tugas_dprd__", "__surat_tugas_asn__",
                                          "__daftar_hadir__", "__undangan_paripurna__"):
                    template_path = template_code

            if not template_path or not os.path.exists(template_path):
                self.after(0, lambda: self._set_preview_status(f"Template untuk '{label}' tidak ditemukan."))
                return

            tmp_docx = tempfile.NamedTemporaryFile(suffix=".docx", delete=False).name
            from docxtpl import DocxTemplate
            doc = DocxTemplate(template_path)
            doc.render(render_ctx)
            doc.save(tmp_docx)

            tmp_pdf = tmp_docx.replace(".docx", ".pdf")
            ok = self._convert_to_pdf(tmp_docx, tmp_pdf)
            if not ok or gen != self._preview_generation:
                return

            pdf_doc = fitz.open(tmp_pdf)
            img_paths = []
            for page_index in range(pdf_doc.page_count):
                if gen != self._preview_generation:
                    pdf_doc.close()
                    return
                page = pdf_doc.load_page(page_index)
                pix = page.get_pixmap(matrix=fitz.Matrix(1.3, 1.3))
                img_path = tmp_pdf.replace(".pdf", f"_p{page_index}.png")
                pix.save(img_path)
                img_paths.append(img_path)
            pdf_doc.close()

            if gen == self._preview_generation:
                self.after(0, lambda: self._apply_preview_images(img_paths, gen))

            for f in (tmp_docx, tmp_pdf):
                try:
                    os.unlink(f)
                except Exception:
                    pass
        except Exception as e:
            self.after(0, lambda: self._set_preview_status(f"Gagal merender preview: {e}"))

    def _convert_to_pdf(self, docx_path, pdf_path):
        if shutil.which("soffice"):
            return self._convert_with_soffice(docx_path, pdf_path)
        if HAS_DOCX2PDF:
            try:
                convert_to_pdf_word(docx_path, pdf_path)
                return os.path.exists(pdf_path)
            except Exception:
                return False
        return False

    def _convert_with_soffice(self, docx_path, pdf_path):
        out_dir = os.path.dirname(docx_path)
        try:
            subprocess.run(
                ["soffice", "--headless", "--convert-to", "pdf", "--outdir", out_dir, docx_path],
                check=True, timeout=30, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            generated_pdf = os.path.splitext(docx_path)[0] + ".pdf"
            if os.path.exists(generated_pdf) and generated_pdf != pdf_path:
                shutil.move(generated_pdf, pdf_path)
            return os.path.exists(pdf_path)
        except Exception:
            return False

    # ------------------------------------------------------------------
    # TAMPILKAN HASIL (DI MAIN THREAD)
    # ------------------------------------------------------------------
    def _apply_preview_images(self, img_paths, gen):
        if gen != self._preview_generation:
            for p in img_paths:
                try:
                    os.unlink(p)
                except Exception:
                    pass
            return

        for widget in self.preview_scroll.winfo_children():
            widget.destroy()
        self.preview_page_labels = []

        try:
            max_w = 360
            for idx, img_path in enumerate(img_paths):
                pil_img = Image.open(img_path)
                ratio = max_w / pil_img.width
                new_size = (max_w, int(pil_img.height * ratio))
                pil_img = pil_img.resize(new_size)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=new_size)

                lbl_nomor = ctk.CTkLabel(self.preview_scroll, text=f"Halaman {idx + 1} / {len(img_paths)}",
                                          font=("Arial", 10, "bold"), text_color="gray")
                lbl_nomor.pack(pady=(10 if idx > 0 else 0, 2))

                img_label = ctk.CTkLabel(self.preview_scroll, image=ctk_img, text="")
                img_label.image = ctk_img
                img_label.pack(pady=(0, 5))

                self.preview_page_labels.append(img_label)

            self._set_preview_status(
                f"Preview diperbarui pukul {time.strftime('%H:%M:%S')} "
                f"({len(img_paths)} halaman)"
            )
        except Exception as e:
            self._set_preview_status(f"Gagal menampilkan preview: {e}")
        finally:
            for p in img_paths:
                try:
                    os.unlink(p)
                except Exception:
                    pass
