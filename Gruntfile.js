banner = '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'

js = [
  'assets/js/**/*.js',
  'tmp/**/*.js'
];
appJs = {
  src: js,
  dest: 'static/app.js'
};
vendorJs = {
  src: [
    'assets/lib/jquery-1.10.1.js',
    'assets/lib/angular.js',
    'assets/lib/**/*.js'
  ],
  dest: 'static/vendor.js'
};
vendorCss = {
  src: ['assets/lib/**/*.css'],
  dest: 'static/vendor.css'
};
partials = 'assets/partials/**/*.html';

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
      dev: {
        options: {
          sassDir: 'assets/scss',
          cssDir: 'static'
        }
      }
    },

    ngtemplates: {
      PlanEvent: {
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