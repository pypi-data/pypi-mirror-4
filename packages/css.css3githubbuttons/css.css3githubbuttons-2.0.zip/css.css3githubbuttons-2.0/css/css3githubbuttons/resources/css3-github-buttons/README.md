# CSS3 GitHub Buttons #

CSS3 GitHub Buttons helps you easily create GitHub-style buttons from links, buttons, and inputs.

Demo: [http://demo.codefusionlab.com/css3-github-buttons/](http://demo.codefusionlab.com/css3-github-buttons/)

## Buttons ##

The "buttons" can be created by adding `class="button"` to any appropriate `<a>`, `<button>`, or `<input>` element. Add a further class of `pill` to create a button pill-like button. Add a further class of `primary` to emphasise more important actions.

    <a href="#" class="button">Post comment (link)</a>
    <input class="button" type="submit" value="Post comment (input)">
    <button class="button" type="submit">Post comment (button)</button>

## Buttons with dangerous actions ##

If you have a button that triggers a dangerous action, like deleting data, this can be indicated by adding the class `danger`.

    <a href="#" class="button danger">Delete post</a>

## Big buttons ##

If you wish to emphasize a specific action you can add the class `big`.

    <a href="#" class="button big">Create Project</a>

## Small buttons ##

Just to complement the `big` class.

    <a href="#" class="button small">Create Project</a>

## Grouped buttons ##

Groups of buttons can be created by wrapping them in an element given a class of `button-group`. A less important group of buttons can be marked out by adding a further class, `minor-group`.

    <div class="button-group minor-group">
        <a href="#" class="button primary">Dashboard</a>
        <a href="#" class="button">Inbox</a>
        <a href="#" class="button">Account</a>
        <a href="#" class="button">Logout</a>
    </div>

## Mixed groups ##

Displaying a mixture of grouped and standalone buttons, as might be seen in a toolbar, can be done by adding another wrapping element with the class `button-container`.

    <div class="actions button-container">
        <a href="#" class="button primary">Compose new</a>

        <div class="button-group">
            <a href="#" class="button primary">Archive</a>
            <a href="#" class="button">Report spam</a>
            <a href="#" class="button danger">Delete</a>
        </div>

        <div class="button-group minor-group">
            <a href="#" class="button">Move to</a>
            <a href="#" class="button">Labels</a>
        </div>
    </div>

## Buttons with icons ##

A range of icons can be added (only for links and buttons) by adding a class of `icon` and any one of the provided icon classes.

    <a href="#" class="button icon search">Search</a>

## Disabled Buttons ##

You can use  `class="disabled"` on any `<a>`, `<button>`, or `<input>` or you can use an attribute - `<input disabled="disabled">`

    <a href="#button" class="button big disabled">Link Disabled</a>
	<input type="submit" class="button big" value="Input Disabled" disabled="disabled" />
	<button class="button big disabled gh-green">Button Disabled</button>

## No Text Buttons ##

Use a button without text (link or button only - does not work on inputs)

    <a href="#button" class="button icon user no-text"></a>
    <button class="button icon user no-text"></button>


## Colored Buttons ##

There are 12 additional colors along with the default and "danger".

Color class names are not in relation to github colors, but a way to ensure they don't conflict with other css

    <a href="#button" class="button">Default</a>
	<a href="#button" class="button gh-red">Red</a>
	<a href="#button" class="button gh-green">Green</a>
	<a href="#button" class="button gh-orange">Orange</a>
	<a href="#button" class="button gh-purple">Purple</a>
	<a href="#button" class="button gh-black">Black</a>
	<a href="#button" class="button gh-white">White</a>
	<a href="#button" class="button gh-pink">Pink</a>
	<a href="#button" class="button gh-lime">Lime</a>
	<a href="#button" class="button gh-yellow">Yellow</a>
	<a href="#button" class="button gh-lblue">Light Blue</a>
	<a href="#button" class="button gh-dblue">Dark Blue</a>

## Browser compatibility ##

Firefox 3.5+, Google Chrome, Safari 4+, IE 8+, Opera 10+.

Note: Some CSS3 features are not supported in older versions of Opera and versions of Internet Explorer prior to IE 8. The use of icons is not supported in IE 6 or IE 7.

## License ##

Public domain: [http://unlicense.org](http://unlicense.org)

## Acknowledgements ##

Inspired by [Michael Henriksen](http://michaelhenriksen.dk)'s [CSS3 Buttons](http://github.com/michenriksen/css3buttons). Icons from [Iconic pack](http://somerandomdude.com/projects/iconic/).

Forked from [necolas] (http://github.com/necolas/css3-github-buttons)