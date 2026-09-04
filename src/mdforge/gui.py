import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .models import ConversionOptions
from .service import ConversionService


class MdForgeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MDForge")
        self.geometry("820x560")
        self.minsize(720, 480)
        self.service = ConversionService()
        self.files: list[Path] = []
        self.output_dir = tk.StringVar(value=str(Path.home() / "Documents" / "MDForge"))
        self.overwrite = tk.BooleanVar(value=False)
        self.source_header = tk.BooleanVar(value=True)
        self._build_ui()

    def _build_ui(self):
        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="MDForge", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(root, text="Converta DOCX, PDF, PPTX, HTML, TXT e MD para Markdown.").pack(anchor="w", pady=(0, 14))

        toolbar = ttk.Frame(root)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Adicionar arquivos", command=self.add_files).pack(side="left")
        ttk.Button(toolbar, text="Limpar", command=self.clear_files).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Pasta de saída", command=self.choose_output).pack(side="left")

        self.listbox = tk.Listbox(root, height=12, selectmode="extended")
        self.listbox.pack(fill="both", expand=True, pady=12)

        output = ttk.Frame(root)
        output.pack(fill="x")
        ttk.Label(output, text="Saída:").pack(side="left")
        ttk.Entry(output, textvariable=self.output_dir).pack(side="left", fill="x", expand=True, padx=8)

        options = ttk.Frame(root)
        options.pack(fill="x", pady=12)
        ttk.Checkbutton(options, text="Sobrescrever existentes", variable=self.overwrite).pack(side="left")
        ttk.Checkbutton(options, text="Incluir comentário com arquivo-fonte", variable=self.source_header).pack(side="left", padx=14)

        action = ttk.Frame(root)
        action.pack(fill="x")
        ttk.Button(action, text="Converter", command=self.convert).pack(side="right")
        self.status = ttk.Label(action, text="Pronto.")
        self.status.pack(side="left")

    def add_files(self):
        patterns = " ".join(f"*{ext}" for ext in self.service.registry.supported_extensions)
        selected = filedialog.askopenfilenames(filetypes=[("Formatos suportados", patterns), ("Todos", "*.*")])
        for item in selected:
            path = Path(item)
            if path not in self.files:
                self.files.append(path)
                self.listbox.insert("end", str(path))

    def clear_files(self):
        self.files.clear()
        self.listbox.delete(0, "end")
        self.status.config(text="Lista limpa.")

    def choose_output(self):
        selected = filedialog.askdirectory(initialdir=self.output_dir.get())
        if selected:
            self.output_dir.set(selected)

    def convert(self):
        if not self.files:
            messagebox.showinfo("MDForge", "Adicione pelo menos um arquivo.")
            return
        options = ConversionOptions(self.source_header.get(), self.overwrite.get())
        results = self.service.convert_many(self.files, Path(self.output_dir.get()), options)
        ok = sum(r.success for r in results)
        failed = len(results) - ok
        self.status.config(text=f"{ok} convertido(s), {failed} falha(s).")
        details = "\n".join(f"{'✓' if r.success else '✗'} {r.source.name}: {r.message}" for r in results)
        messagebox.showinfo("Resultado", details)


def main():
    app = MdForgeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
