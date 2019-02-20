call venv/Scripts/activate
rm -rf src/ui/*
FOR %%I in (ui\*.*) DO (
	echo Converting %%I
	call pyuic5 %%I >> src/ui/%%~nI.py
)
