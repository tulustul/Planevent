'use strict';

var banner =
  '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n';

var js = [
    'assets/js/**/*.js',
    'tmp/partials.js'
];
var appJs = {
    src: js,
    dest: 'static/app.js'
};
var appProdJs = {
    src: 'tmp/**/*.js',
    dest: 'static/app.js'
};
var vendorJs = {
    src: [
        'bower_components/jquery/dist/jquery.js',
        'bower_components/jquery-ui/ui/jquery-ui.js',
        // 'bower_components/jquery-ui/ui/jquery.ui.core.js',
        // 'bower_components/jquery-ui/ui/jquery.ui.widget.js',
        // 'bower_components/jquery-ui/ui/jquery.ui.slider.js',

        'bower_components/underscore/underscore.js',

        'bower_components/angular/angular.js',
        'bower_components/angular-animate/angular-animate.js',
        'bower_components/angular-resource/angular-resource.js',
        'bower_components/angular-route/angular-route.js',

        'bower_components/angucomplete/angucomplete.js',
        'bower_components/ngAutocomplete/src/ngAutocomplete.js',
        'bower_components/angular-bootstrap/ui-bootstrap-tpls.js',
        'bower_components/angular-ui-slider/src/slider.js',
        'bower_components/ng-file-upload/angular-file-upload.js',
        'bower_components/ng-table/ng-table.js',
        'bower_components/flexslider/jquery.flexslider.js',
        'bower_components/angular-flexslider/angular-flexslider.js'
    ],
    dest: 'static/vendor.js'
};
var vendorCss = {
    src: [
        'bower_components/bootstrap/dist/css/bootstrap.css',
        'bower_components/bootstrap/dist/css/bootstrap-theme.css',
        'bower_components/jquery-ui/themes/base/jquery-ui.css',
        'bower_components/angucomplete/angucomplete.css',
        'bower_components/flexslider/flexslider.css'
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
            app: appProdJs,
            vendor: vendorJs,
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
                    cssDir: 'static',
                    specify: [
                        'assets/scss/main.scss',
                        'assets/scss/admin.scss'
                    ]
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

        cssmin: {
            minify: {
                expand: true,
                src: 'static/*.css',
                dest: '.'
            }
        },

        ngmin: {
            app: {
                expand: true,
                src: ['assets/js/*.js'],
                dest: 'tmp'
            }
        },

        watch: {
            js: {
                files: ['assets/js/**/*.js'].concat([partials]),
                tasks: ['ngtemplates', 'concat']
            },
            scss: {
                files: 'assets/scss/*.scss',
                tasks: 'compass'
            }
        },

        clean: ['tmp']

    });

    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-ngmin');
    grunt.loadNpmTasks('grunt-angular-templates');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-clean');

    grunt.registerTask('staging', [
        'ngtemplates',
        'concat',
        'compass',
        'clean'
    ]);

    grunt.registerTask('dev', [
        'ngtemplates',
        'concat',
        'compass',
        'watch',
        'clean'
    ]);

    grunt.registerTask('prod', [
        'ngtemplates',
        'concat',
        'ngmin',
        'uglify',
        'compass',
        'cssmin',
        'clean'
    ]);
};
