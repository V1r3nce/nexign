properties([parameters([
    choice(name: 'headless', choices: ['False', 'True'], description: 'Режим браузера (с GUI или без)')
])])

CRON_SETTINGS = BRANCH_NAME == "master" ? '''0 0 * * * % headless==False''' : ""

pipeline {
    agent any
    triggers {
        parameterizedCron(CRON_SETTINGS)
    }

    stages {
        stage('Build and Run') {
            steps {
                script {
                    // Загрузка образа Docker.  Если образ не найден локально, он будет скачан.
                    docker.image('docker.nexign.com/node:16').pull('always')

                    // Создание контейнера Docker.  -v монтирует текущий рабочий каталог Jenkins в контейнер.
                    // -w устанавливает рабочий каталог внутри контейнера.
                    // Замените 'your_python_script.py' на имя вашего скрипта.
                    def containerId = docker.run(
                        image: 'docker.nexign.com/node:16',
                        args: '-w /tmp /bin/bash -c "python main.py"',
                        volumes: [[hostPath: '.', containerPath: '/tmp']],
                        remove: true
                    ).id

                    // Вывод логов из контейнера.  Это может быть полезно для отладки.
                    def logs = sh(script: "docker logs ${containerId}", returnStdout: true)
                    echo logs

                    // Проверка на ошибки.  Если скрипт завершился с кодом ошибки, Jenkins остановит pipeline.
                    if (logs.exitCode != 0) {
                        error("Python script failed with exit code: ${logs.exitCode}")
                    }
                }
            }
        }
    }
}