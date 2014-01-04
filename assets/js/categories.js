var lastCategoryId = 0;

function makeCategory(icon) {
    lastCategoryId += 1;
    return {
        id: lastCategoryId,
        iconPath: '/static/images/icons/' + icon
    };
}

var categories = {
    // add categories only to the end of the list
    'Hotele': makeCategory('question.png'),
    'Catering': makeCategory('question.png'),
    'Transport': makeCategory('question.png'),
    'Sale': makeCategory('question.png'),
    'Sport': makeCategory('question.png')
};
