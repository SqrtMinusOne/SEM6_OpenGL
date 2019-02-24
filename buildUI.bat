call venv\Scripts\activate
IF EXIST src\ui (
    rm -rf src\ui\*
) ELSE (
    md src\ui
)
FOR %%I in (ui\*.*) DO (
	echo Converting %%I
	call pyuic5 %%I >> src\ui\%%~nI.py
)
echo Finished