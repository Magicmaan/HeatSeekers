echo %cd%
start "" node-red && (
  echo starting Node-Red
) || (
  echo Node-Red not found
)

timeout /t 5 /nobreak
rem Open the URL in the default web browser
start http://127.0.0.1:1880
start http://127.0.0.1:1880/ui