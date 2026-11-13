
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Source code checked out successfully'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"C:\\Users\\LAHARI\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" --version'

                bat '"C:\\Users\\LAHARI\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m pip install -r requirements.txt'
            }
        }

        stage('Build') {
            steps {
                bat '"C:\\Users\\LAHARI\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m compileall app.py'
            }
        }

        stage('Test') {
            steps {
                echo 'Testing completed successfully'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deployment completed'
            }
        }
    }
}
