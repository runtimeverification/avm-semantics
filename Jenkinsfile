pipeline {
  agent { label 'docker' }
  environment {
    VERSION   = '0.1.0'
    LONG_REV  = """${sh(returnStdout: true, script: 'git rev-parse HEAD').trim()}"""
    SHORT_REV = """${sh(returnStdout: true, script: 'git rev-parse --short=7 HEAD').trim()}"""
    K_VERSION = """${sh(returnStdout: true, script: 'cd deps/k && git tag --points-at HEAD | cut --characters=2-').trim()}"""
  }
  options { ansiColor('xterm') }
  stages {
    stage('Init title') {
      when { changeRequest() }
      steps { script { currentBuild.displayName = "PR ${env.CHANGE_ID}: ${env.CHANGE_TITLE}" } }
    }
    stage('Build and Test') {
      agent {
        dockerfile {
          additionalBuildArgs '--build-arg K_COMMIT="${K_VERSION}" --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
          reuseNode true
        }
      }
      stages {
        stage('Build') { steps { sh 'make build -j4' } }
        stage('Test kavm') {
          failFast true
          options { timeout(time: 10, unit: 'MINUTES') }
          parallel {
            stage('Parse TEAL progams') { steps { sh 'make -j4 test-kavm-kast-teal' } }
            stage('Parse AVM scenarios') { steps { sh 'make -j4 test-kavm-kast-avm-scenario' } }
          }
        }
        stage('Test AVM Semantics') {
          failFast true
          options { timeout(time: 20, unit: 'MINUTES') }
          parallel {
            stage('Test kavm.algod') { steps { sh 'make -j4 test-kavm-algod' } }
            stage('Test KAVM hooks') { steps { sh 'make build-kavm-hooks-tests' } }
            stage('AVM tests') { steps { sh 'make -j4 test-avm-semantics' } }
            stage('Module Imports Graph') { steps { sh 'make module-imports-graph' } }
          }
        }
      }
    }
    stage('Deploy') {
      agent {
        dockerfile {
          additionalBuildArgs '--build-arg K_COMMIT="${K_VERSION}" --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
          reuseNode true
        }
      }
      when {
        branch 'master'
        beforeAgent true
      }
      stages {
        stage('Update Dependents') {
          steps {
            build job: 'DevOps/master', propagate: false, wait: false                                                     \
                , parameters: [ booleanParam ( name: 'UPDATE_DEPS'         , value: true                                ) \
                              , string       ( name: 'UPDATE_DEPS_REPO'    , value: 'runtimeverification/avm-semantics' ) \
                              , string       ( name: 'UPDATE_DEPS_VERSION' , value: "${env.LONG_REV}")                    \
                              ]
          }
        }
      }
    }
  }
}
