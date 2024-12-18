// == Параметры для настройки под проект ==

// IP используемого виртуального сервера на стенде
def openvpn_ping_server = '192.168.10.89'

// Label для выбора агента в Jenkins
def agent_label = '(woi-rhel8 && docker) || woi-tmp-rhel8-docker'

// Идентификатор (ID) credentials для Git в Jenkins
def git_credentials_id = 'mops_ssh'

// Стенд, используемый по умолчанию для запуска тестов
def default_clone_name = 'nbss-redos-masirebe'

// Мастер-стенд
def master_name = 'nbss-redos-root'

// Репозиторий с конфигурациями для OpenVPN
def openvpn_repo = 'ssh://git@gitlab.nexign.com:2222/internal/mfclones/mors.git'

// URL c UI, используемый по умолчанию для запуска тестов на клонах
def default_clone_base_url = 'http://srv-app02.nbss-redos-root.cloud.billing.ru:47225/rm-ui/all'

// == Константы для стиля разделителей в параметрах сборки ==

def separator_section_header_style = """
	background-color: #bff04e;
	text-align: center;
	padding: 4px;
	color: #343434;
    font-size: 22px;
	font-weight: normal;
	text-transform: uppercase;
	font-family: Open Sans, sans-serif;
	letter-spacing: 1px;
	font-style: italic;
"""
def separator_style = "border-width: 0"

pipeline {
    agent {
        label agent_label
    }
    options {
        timestamps ()
    }

    parameters {
        separator(name: "test_parameters", sectionHeader: "Test list and Selenium parameters",
                separatorStyle: separator_style, sectionHeaderStyle: separator_section_header_style)

        string(name: 'tests_branch', defaultValue: 'master', description: 'UI tests repo branch')

        booleanParam(name: 'use_openvpn', defaultValue: false, description: 'Check to use openvpn')

        separator(name: "cloud_parameters", sectionHeader: "Test stand parameters",
                separatorStyle: separator_style, sectionHeaderStyle: separator_section_header_style)

        string(name: 'SOLO_STAND', defaultValue: '', description: 'Solo stand name')

        string(name: 'openvpn_branch', defaultValue: 'master', description: 'OPENVPN branch')
        string(name: 'CLONE_NAME', defaultValue: default_clone_name, description: 'Stand name')

    }

    environment{
        USE_OPENVPN = "${params.use_openvpn}"
        TEST_SOLO_URL = "http://srv-app02.${params.SOLO_STAND}.res.nxcloud.nexign.com:47225/rm-ui/all";
        USER=credentials('USER')
        USER_LOGIN="${USER_USR}"
        USER_PASS="${USER_PSW}"
    }
    stages {
        stage('Set build name') {
            steps {
                script {
                    if (params.use_openvpn == true) {
                        currentBuild.displayName = "#${BUILD_NUMBER} ${CLONE_NAME}"
                    }
                    else {
                        currentBuild.displayName = "#${BUILD_NUMBER} ${SOLO_STAND}"
                    }
                }
            }
        }
        stage('Clean workspace') {
            steps {
                echo '--- Clean workspace ---'
                cleanWs deleteDirs:true
            }
        }
        stage ('Get OpenVPN config sources') {
            when { expression { params.use_openvpn } }
            steps {
                echo '--- Get OpenVPN config sources ---'
                dir("openvpn_configs") {
                    git branch: "master", credentialsId: "${git_credentials_id}", url: "${openvpn_repo}"
                }
            }
        }
        stage ('Prepare OpenVPN connection') {
            when { expression { params.use_openvpn } }
            steps {
                echo '--- Prepare OpenVPN connection ---'

                script {
                    sh '''
                        echo "Connecting to clone ${CLONE_NAME} by openvpn.."
                        export STEPS_PATH=$(pwd)
                        export OPENVPN_RUNNING_PIDS=$(pgrep -d ' ' -f 'openvpn')
                        if [ -z "$OPENVPN_RUNNING_PIDS" ]; then
                            echo "no running openvpn instances to kill"
                            rm -rf /tmp/ansible-*
                        else
                            echo "killing openvpn running instances $OPENVPN_RUNNING_PIDS"
                            sudo kill $OPENVPN_RUNNING_PIDS
                            rm -rf /tmp/ansible-*
                        fi

                        mkdir -p $WORKSPACE/ansible-tmp $WORKSPACE/vpnlog
                        pwd
                        cd $WORKSPACE/openvpn_configs/openvpn/${CLONE_NAME}
                        ls -lhR
                        sudo openvpn --daemon --config ${CLONE_NAME}.ovpn --log /tmp/vpnlog/openvpn.log
                    '''

                    sh """
                        echo "Check openvpn clone connection"
                        ping -c 3 ${openvpn_ping_server}
                        if [ \$? -eq 0 ]; then
                            echo "Now connected to \${CLONE_NAME} via OpenVPN"
                        else
                            echo "Openvpn connection error!"
                            echo "Please, check that the 'CLONE_NAME' parameter is set correctly and the openvpn config is correct"
                            exit -1
                        fi
                    """
                }
            }
        }
        stage ('Get UI Tests') {
            steps {
                echo '--- Get UI Tests ---'
                dir("ui-tests") {
                    git branch: params.tests_branch, credentialsId: 'mops_ssh', url: "ssh://git@gitlab.nexign.com:2222/products/uds/selenium-python-tests.git"
                }
            }
        }
        stage("Run tests") {
            steps {
                script {
                    try {
                        docker.image('docker.nexign.com/playwright/python:latest').inside {
                            sh """
                               cd ui-tests
                               pip install -r requirements.txt
                               playwright install chrome
                            """
                            if (params.use_openvpn == true) {
                                sh """
                                    cd ui-tests
                                    export BASE_URL=${default_clone_base_url}
                                    python3 -m pytest --headless --alluredir=${WORKSPACE}/allure-results
                                """
                            }
                            else {
                                sh """
                                    cd ui-tests
                                    export BASE_URL=${TEST_SOLO_URL}
                                    python3 -m pytest --headless --alluredir=${WORKSPACE}/allure-results
                                """
                            }
                        } catch (error) {}
                    }
                }
            }
        }
        stage('Allure Report') {
            steps {
                allure commandline: 'allure-2.18.1', includeProperties: false, jdk: '', results: [[path: '${WORKSPACE}/allure-results']]
            }
        }
    }
    post {
        success {
            cleanWs deleteDirs:true
        }
    }
}
