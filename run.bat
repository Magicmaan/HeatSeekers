echo %cd%


rem Start the Python file in another window using the virtual environment
(
  start %cd%\env\Scripts\python %cd%\src\main.py
) || (
  echo Failed to start Python script automatically
  echo Please start the Python script manually by running the following command:
  echo %cd%\env\Scripts\python %cd%\src\main.py
)

start "" node-red %cd%/.node-red/flows.json && (
  echo starting Node-Red
) || (
  echo Node-Red not found
)

timeout /t 5 /nobreak
rem Open the URL in the default web browser
start http://127.0.0.1:1880
start http://127.0.0.1:1880/dashboard

