'use strict';

var banner =
  '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n';

var js = [
    'assets/js/**/*.js',
    'tmp/**/*.js'
];
var appJs = {
    src: js,
    dest: 'static/app.js'
};
var vendorJs = {
    src: [
        'bower_components/jquery/jquery.js',
        'bower_components/underscore/underscore.js',
        'bower_components/angular/angular.js',
        'bower_components/angular-animate/angular-animate.js',
        'bower_components/angular-resource/angular-resource.js',
        'bower_components/angular-bootstrap/ui-bootstrap-tpls.js',
        'bower_components/angular-file-upload/angular-file-upload.js',
        'bower_components/angular-route/angular-route.js',
        'bower_components/ng-table/ng-table.js',
        'bower_components/ngInfiniteScroll/ng-infinite-scroll.js',
    ],
    dest: 'static/vendor.js'
};
var vendorCss = {
    src: [
        'bower_components/bootstrap/dist/css/bootstrap.css',
        'bower_components/bootstrap/dist/css/bootstrap-theme.css'
    ],
    dest: 'static/vendor.css'
};
var partials = 'assets/partials/**/*.html';
module.exports = function(grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        uglify: {
            options: {
                banner: banner
            },
            app: appJs,
            vendor: vendorJs
        },

        concat: {
            options: {
                banner: banner
            },
            app: appJs,
            vendor: vendorJs,
            vendorCss: vendorCss
        },

        compass: {
            require: 'susy',
            dev: {
                options: {
                    sassDir: 'assets/scss',
                    cssDir: 'static'
                }
            }
        },

        ngtemplates: {
            planevent: {
                options:    {
                    base: 'assets/partials',
                    htmlmin: {}
                },
                src: partials,
                dest: 'tmp/partials.js'
            }
        },

        watch: {
            js: {
                files: js.concat([partials]),
                tasks: ['ngtemplates', 'concat']
            },
            scss: {
                files: 'assets/scss/*.scss',
                tasks: 'compass'
            }
        },

    });

    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-watch');
    // grunt.loadNpmTasks('grunt-ngmin');
    grunt.loadNpmTasks('grunt-angular-templates');
    grunt.loadNpmTasks('grunt-contrib-compass');

    grunt.registerTask('dev', ['ngtemplates', 'concat', 'compass', 'watch']);
    grunt.registerTask('prod', ['ngtemplates', 'uglify', 'compass', 'watch']);
};
