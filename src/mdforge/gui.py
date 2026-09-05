import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .converters.xlsx import XlsxConverter
from .models import ConversionOptions
from .service import ConversionService

try:  # Arrastar e soltar é opcional; a GUI funciona sem a dependência.
    from tkinterdnd2 import DND_FILES, TkinterDnD

    _DND_AVAILABLE = True
except Exception:  # pragma: no cover - depende do ambiente
    DND_FILES = None
    TkinterDnD = None
    _DND_AVAILABLE = False

_ALL_SHEETS = "(todas as abas)"


class MdForgeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MDForge")
        self.geometry("820x620")
        self.minsize(720, 540)
        self.service = ConversionService()
        self.files: list[Path] = []
        self.output_dir = tk.StringVar(value=str(Path.home() / "Documents" / "MDForge"))
        self.output_name = tk.StringVar()
        self.sheet_name = tk.StringVar(value=_ALL_SHEETS)
        self.overwrite = tk.BooleanVar(value=False)
        self.source_header = tk.BooleanVar(value=True)
        self._dnd_enabled = self._enable_dnd()
        self._build_ui()

    def _enable_dnd(self) -> bool:
        if not _DND_AVAILABLE:
            return False
        try:
            self.TkdndVersion = TkinterDnD._require(self)
            return True
        except Exception:  # pragma: no cover - depende do ambiente
            return False

    def _build_ui(self):
        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="MDForge", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(root, text="Converta DOCX, PDF, PPTX, HTML, TXT, XLSX e MD para Markdown.").pack(anchor="w", pady=(0, 14))

        toolbar = ttk.Frame(root)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Adicionar arquivos", command=self.add_files).pack(side="left")
        ttk.Button(toolbar, text="Remover selecionados", command=self.remove_selected).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Limpar", command=self.clear_files).pack(side="left")
        ttk.Button(toolbar, text="Pasta de saída", command=self.choose_output).pack(side="left", padx=8)

        hint = "Arraste e solte arquivos aqui ou use \"Adicionar arquivos\"." if self._dnd_enabled \
            else "Use \"Adicionar arquivos\" (arrastar e solte requer o pacote tkinterdnd2)."
        ttk.Label(root, text=hint, foreground="#666").pack(anchor="w", pady=(10, 0))

        self.listbox = tk.Listbox(root, height=10, selectmode="extended")
        self.listbox.pack(fill="both", expand=True, pady=(4, 12))
        self.listbox.bind("<<ListboxSelect>>", lambda _e: None)
        if self._dnd_enabled:
            self.listbox.drop_target_register(DND_FILES)
            self.listbox.dnd_bind("<<Drop>>", self._on_drop)

        output = ttk.Frame(root)
        output.pack(fill="x")
        ttk.Label(output, text="Pasta de saída:").pack(side="left")
        ttk.Entry(output, textvariable=self.output_dir).pack(side="left", fill="x", expand=True, padx=8)

        name_row = ttk.Frame(root)
        name_row.pack(fill="x", pady=(10, 0))
        ttk.Label(name_row, text="Nome do arquivo (.md):").pack(side="left")
        ttk.Entry(name_row, textvariable=self.output_name).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Label(name_row, text="(apenas 1 arquivo)", foreground="#666").pack(side="left")

        self.sheet_row = ttk.Frame(root)
        self.sheet_row.pack(fill="x", pady=(10, 0))
        ttk.Label(self.sheet_row, text="Aba do Excel:").pack(side="left")
        self.sheet_combo = ttk.Combobox(
            self.sheet_row, textvariable=self.sheet_name, state="readonly", values=[_ALL_SHEETS]
        )
        self.sheet_combo.pack(side="left", fill="x", expand=True, padx=8)
        self._set_sheet_row_visible(False)

        options = ttk.Frame(root)
        self.options_frame = options
        options.pack(fill="x", pady=12)
        ttk.Checkbutton(options, text="Sobrescrever existentes", variable=self.overwrite).pack(side="left")
        ttk.Checkbutton(options, text="Incluir comentário com arquivo-fonte", variable=self.source_header).pack(side="left", padx=14)

        action = ttk.Frame(root)
        action.pack(fill="x")
        ttk.Button(action, text="Converter", command=self.convert).pack(side="right")
        self.status = ttk.Label(action, text="Pronto.")
        self.status.pack(side="left")

    def _set_sheet_row_visible(self, visible: bool):
        if visible:
            self.sheet_row.pack(fill="x", pady=(10, 0), before=self.options_frame)
        else:
            self.sheet_row.pack_forget()

    def _add_path(self, path: Path) -> bool:
        if path not in self.files and path.is_file():
            self.files.append(path)
            self.listbox.insert("end", str(path))
            return True
        return False

    def _on_drop(self, event):
        # A lista vem entre chaves quando há espaços no caminho.
        added = 0
        for item in self.tk.splitlist(event.data):
            if self._add_path(Path(item)):
                added += 1
        self._refresh_dynamic_fields()
        self.status.config(text=f"{added} arquivo(s) adicionado(s).")

    def add_files(self):
        patterns = " ".join(f"*{ext}" for ext in self.service.registry.supported_extensions)
        selected = filedialog.askopenfilenames(filetypes=[("Formatos suportados", patterns), ("Todos", "*.*")])
        for item in selected:
            self._add_path(Path(item))
        self._refresh_dynamic_fields()

    def remove_selected(self):
        for index in sorted(self.listbox.curselection(), reverse=True):
            self.listbox.delete(index)
            del self.files[index]
        self._refresh_dynamic_fields()
        self.status.config(text="Removido(s).")

    def clear_files(self):
        self.files.clear()
        self.listbox.delete(0, "end")
        self._refresh_dynamic_fields()
        self.status.config(text="Lista limpa.")

    def choose_output(self):
        selected = filedialog.askdirectory(initialdir=self.output_dir.get())
        if selected:
            self.output_dir.set(selected)

    def _refresh_dynamic_fields(self):
        # Sugere o nome de saída quando há exatamente um arquivo.
        if len(self.files) == 1:
            self.output_name.set(self.files[0].stem)
        else:
            self.output_name.set("")

        # Mostra o seletor de aba apenas para um único arquivo Excel.
        excel = None
        if len(self.files) == 1:
            converter = self.service.registry.get(self.files[0])
            if isinstance(converter, XlsxConverter):
                excel = (converter, self.files[0])

        if excel is None:
            self.sheet_name.set(_ALL_SHEETS)
            self.sheet_combo.configure(values=[_ALL_SHEETS])
            self._set_sheet_row_visible(False)
            return

        converter, path = excel
        try:
            names = converter.sheet_names(path)
        except Exception as exc:
            self.status.config(text=f"Não foi possível ler as abas: {exc}")
            names = []
        self.sheet_combo.configure(values=[_ALL_SHEETS, *names])
        self.sheet_name.set(_ALL_SHEETS)
        self._set_sheet_row_visible(True)

    def convert(self):
        if not self.files:
            messagebox.showinfo("MDForge", "Adicione pelo menos um arquivo.")
            return
        sheet = self.sheet_name.get()
        options = ConversionOptions(
            include_source_header=self.source_header.get(),
            overwrite=self.overwrite.get(),
            output_name=self.output_name.get().strip() or None,
            sheet_name=None if sheet in ("", _ALL_SHEETS) else sheet,
        )
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
