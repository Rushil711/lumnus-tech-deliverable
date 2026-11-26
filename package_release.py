"""Create a clean, reproducible-to-inspect sharing package (no credentials or records)."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parent
out=root.parent/'Lumnus-Outreach-Studio.zip'
exclude={'data','__pycache__','.git','.DS_Store','enterprise-reference-seed.py','requirements','workspace-preview.jpg','mobile-preview.jpg','report-preview.jpg'}
with ZipFile(out,'w',ZIP_DEFLATED) as archive:
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if p.is_file() and not any(part in exclude or (part.startswith('.env') and part!='.env.example') for part in rel.parts) and p.suffix not in {'.pyc','.zip'}:
   archive.write(p,Path('lumnus-outreach')/rel)
with ZipFile(out) as archive:
 assert archive.testzip() is None
 assert not any('/data/' in n or n.endswith('/.env') for n in archive.namelist())
 print(f'Packaged {len(archive.namelist())} files: {out}')
