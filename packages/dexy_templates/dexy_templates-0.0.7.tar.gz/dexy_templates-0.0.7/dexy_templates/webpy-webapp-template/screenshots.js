/// @export "setup"
var casper = require('casper').create({
    viewportSize : {width : 800, height : 300}
});

/// @export "initial"
casper.start("http://localhost:8080", function() {
    this.wait(500);
    this.capture("index.pdf");
    this.capture("index.png");
});

/// @export "add-todo"
casper.then(function() {
    this.fill("form", {
        "title": "create web app dexy demo"
    }, true);
    this.capture("add.png");
    this.capture("add.pdf");
});

/// @export "created-todo"
casper.then(function() {
    this.capture("added.png");
    this.capture("added.pdf");
});

/// @export "delete-todo"
casper.then(function() {
    this.click("input");
});

casper.then(function() {
    this.capture("deleted.png");
    this.capture("deleted.pdf");
});

/// @export "run"
casper.run();
