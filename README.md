# PMTools_plt
Plotly version of [PMTools](https://github.com/I194/PMTools)

![image](https://user-images.githubusercontent.com/49840874/140026950-abf3d8f3-9265-479e-a2cb-9ce231d873b2.png)

**Alpha** версия программы [PMTools](https://github.com/I194/PMTools). 

В проекте используются:
1. **Python 3**
2. [**Plotly**](https://plotly.com/python/)
3. [**Dash.Plotly**](https://dash.plotly.com/)

А также **Pandas**, **Numpy** и различные библиотеки для статистической обработки данных (в частности - [**PmagPy**](https://github.com/PmagPy/PmagPy)).

![image](https://user-images.githubusercontent.com/49840874/140027549-884ba73a-4ed8-4d06-8266-7bbad0a85313.png)

# Установка PMTools
:exclamation: PMTools доступна только для Windows. 

Скачайте следующий архив ```PMTools v. alpha.rar``` c [Google Drive](https://drive.google.com/file/d/1uoA2qVxozb0JqOzDsjdhXzt4fUxjX6qh/view). Архив распакуйте в одну папку. Запустите ```gtk3-runtime-3.24.11-2019-10-04-ts-win64.exe```, начнётся процесс его установки. Далее, соглашаясь со всеми стандартными параметрами установки, установите его. В папке ```PMTools v. alpha``` найдите ```PMTools.exe``` и запустите его. Откроется отладочная консоль, а затем сама программа в выбранном по умолчанию браузере. Чтобы закрыть программу необходимо закрыть отладочную консоль. 

:exclamation: Без установки **gtk3** экспорт графиков из PMTools не будет работать корректно. Связано это в первую очередь с тем, что по заказу требовалось обязательное наличие оффлайн экспорта, которое, однако, у Plotly было реализовано крайне плохо на момент разработки и потому использовалась Orca. 

# Тестовые данные
Протестировать PMTools вы можете данными из следующих файлов: [006.PMD](https://github.com/I194/PMTools_plt/blob/master/006.PMD) и [15-af.pmd](https://github.com/I194/PMTools_plt/blob/master/15-af.pmd). 

***
# История и планы 

Внутренняя логика программы написана на python3.7, графики и диаграммы строятся при помощи библиотеки [Plotly](https://plotly.com/python/). Интерфейс создан при помощи [**Dash.Plotly**](https://dash.plotly.com/). Для некоторых алгоритмов используется [PmagPy](https://earthref.org/PmagPy/). 

Поскольку это alpha версия, некоторые алгоритмы могут работать неправильно и иногда давать некорректные результаты. Скорость работы большинства алгоритмов оставляет желать лучшего, связано это с множеством факторов и в будущем это будет обязательно исправлено.

Сейчас доступна только десктопная версия PMTools, хотя изначально разрабатывался именно сайт PMTools. Разработка этого сайта временно приостановлена и будет возобновлена после решения некоторых проблем, связанных с построением графиков. После этого, скорее всего, будет осуществлён переход с python3.7 на C++ (в первую очередь, для повышения производительности) и создана полноценная десктопная версия PMTools.
***
