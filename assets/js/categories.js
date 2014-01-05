function makeCategory(name, icon) {
    return {
        name: name,
        iconPath: '/static/images/icons/' + icon
    };
}

var categories = [
    // add categories only to the end of the list
    makeCategory('Hotele', 'question.png'),
    makeCategory('Catering', 'question.png'),
    makeCategory('Transport', 'question.png'),
    makeCategory('Sale', 'question.png'),
    makeCategory('Sport', 'question.png')
];
