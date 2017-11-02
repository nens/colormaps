node{
    stage "Checkout"
    checkout scm

    stage "Build"
    sh "docker-compose build"
    sh "docker-compose run lib buildout -vvvvv"

    stage "Pep 8"
    sh "if docker-compose run lib bin/pep8 colormaps > pep8.txt; then echo 'pep8 is a success'; else cat pep8.txt; false; fi"

    stage "Test"
    sh "docker-compose run lib bin/test"
}
