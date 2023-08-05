# CSS3 GitHub Buttons Extended All (Colors, Icons, Sizes) #

## This includes the base Css3 Github Buttons, as well as the Extended Colors, Sizes, and Icons pack ##

CSS3 GitHub Buttons helps you easily create GitHub-style buttons from links, buttons, and inputs.

Demo: [demo.codefusionlab.com/css3-github-buttons/](http://demo.codefusionlab.com/css3-github-buttons/)

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


## Sizes ##

Demo: [http://demo.codefusionlab.com/css3-github-buttons/ext_button_size/](http://demo.codefusionlab.com/css3-github-buttons/ext_button_size/)

These are all incremented by px sizes

    <a href="#button" class="button bigger">bigger</a>
    <a href="#button" class="button biggest">biggest</a>
    <a href="#button" class="button xl">xl</a>
    <a href="#button" class="button xxl">xxl</a>
    <a href="#button" class="button xxxl">xxxl</a>
    <a href="#button" class="button xxxxl">xxxxl</a>
    <a href="#button" class="button xxxxxl">xxxxxl</a>

These are all incremented by em sizes

    <a href="#button" class="button x1">x1</a>
    <a href="#button" class="button x2">x2</a>
    <a href="#button" class="button x3">x3</a>
    <a href="#button" class="button x4">x4</a>
    <a href="#button" class="button x5">x5</a>
    <a href="#button" class="button x6">x6</a>
    <a href="#button" class="button x7">x7</a>
    <a href="#button" class="button x8">x8</a>
    <a href="#button" class="button x9">x9</a>
    <a href="#button" class="button x10">x10</a>

These are all fixed min-widths by px

    <a href="#button" class="button minwidth50">minwidth50</a>
    <a href="#button" class="button minwidth100">minwidth100</a>
    <a href="#button" class="button minwidth150">minwidth150</a>
    <a href="#button" class="button minwidth200">minwidth200</a>
    <a href="#button" class="button minwidth250">minwidth250</a>
    <a href="#button" class="button minwidth300">minwidth300</a>
    <a href="#button" class="button minwidth350">minwidth350</a>
    <a href="#button" class="button minwidth400">minwidth400</a>
    <a href="#button" class="button minwidth450">minwidth450</a>
    <a href="#button" class="button minwidth500">minwidth500</a>
    <a href="#button" class="button minwidth550">minwidth550</a>
    <a href="#button" class="button minwidth600">minwidth600</a>
    <a href="#button" class="button minwidth650">minwidth650</a>
    <a href="#button" class="button minwidth700">minwidth700</a>
    <a href="#button" class="button minwidth750">minwidth750</a>
    <a href="#button" class="button minwidth800">minwidth800</a>
    <a href="#button" class="button minwidth850">minwidth850</a>
    <a href="#button" class="button minwidth900">minwidth900</a>
    <a href="#button" class="button minwidth950">minwidth950</a>

These are all fluid min-widths by %

    <a href="#button" class="button minpcent25">minpcent25</a>
    <a href="#button" class="button minpcent50">minpcent50</a>
    <a href="#button" class="button minpcent75">minpcent75</a>
    <a href="#button" class="button minpcent100">minpcent100</a>

These are all fixed max-widths by px

    <a href="#button" class="button maxwidth50">maxwidth50</a>
    <a href="#button" class="button maxwidth100">maxwidth100</a>
    <a href="#button" class="button maxwidth150">maxwidth150</a>
    <a href="#button" class="button maxwidth200">maxwidth200</a>
    <a href="#button" class="button maxwidth250">maxwidth250</a>
    <a href="#button" class="button maxwidth300">maxwidth300</a>
    <a href="#button" class="button maxwidth350">maxwidth350</a>
    <a href="#button" class="button maxwidth400">maxwidth400</a>
    <a href="#button" class="button maxwidth450">maxwidth450</a>
    <a href="#button" class="button maxwidth500">maxwidth500</a>
    <a href="#button" class="button maxwidth550">maxwidth550</a>
    <a href="#button" class="button maxwidth600">maxwidth600</a>
    <a href="#button" class="button maxwidth650">maxwidth650</a>
    <a href="#button" class="button maxwidth700">maxwidth700</a>
    <a href="#button" class="button maxwidth750">maxwidth750</a>
    <a href="#button" class="button maxwidth800">maxwidth800</a>
    <a href="#button" class="button maxwidth850">maxwidth850</a>
    <a href="#button" class="button maxwidth900">maxwidth900</a>
    <a href="#button" class="button maxwidth950">maxwidth950</a>

These are all fluid max-widths by %

    <a href="#button" class="button maxpcent25">maxpcent25</a>
    <a href="#button" class="button maxpcent50">maxpcent50</a>
    <a href="#button" class="button maxpcent75">maxpcent75</a>
    <a href="#button" class="button maxpcent100">maxpcent100</a>

use this if want your text to wrap

    <a href="#button" class="button maxwrap">maxwrap</a>





## Extended Icons ##

Demo: [http://demo.codefusionlab.com/css3-github-buttons/ext_button_icons/](http://demo.codefusionlab.com/css3-github-buttons/ext_button_icons/)

    <a href="#button" class="button icon ampersand">ampersand</a>
    <a href="#button" class="button icon aperture">aperture</a>
    <a href="#button" class="button icon aperture_alt">aperture_alt</a>
    <a href="#button" class="button icon arrow_down">arrow_down</a>
    <a href="#button" class="button icon arrow_down_alt1">arrow_down_alt1</a>
    <a href="#button" class="button icon arrow_down_alt2">arrow_down_alt2</a>
    <a href="#button" class="button icon arrow_left">arrow_left</a>
    <a href="#button" class="button icon arrow_left_alt1">arrow_left_alt1</a>
    <a href="#button" class="button icon arrow_left_alt2">arrow_left_alt2</a>
    <a href="#button" class="button icon arrow_right">arrow_right</a>
    <a href="#button" class="button icon arrow_right_alt1">arrow_right_alt1</a>
    <a href="#button" class="button icon arrow_right_alt2">arrow_right_alt2</a>
    <a href="#button" class="button icon arrow_up">arrow_up</a>
    <a href="#button" class="button icon arrow_up_alt1">arrow_up_alt1</a>
    <a href="#button" class="button icon arrow_up_alt2">arrow_up_alt2</a>
    <a href="#button" class="button icon article">article</a>
    <a href="#button" class="button icon at">at</a>
    <a href="#button" class="button icon award_fill_alt1">award_fill_alt1</a>
    <a href="#button" class="button icon award_stroke_alt1">award_stroke_alt1</a>
    <a href="#button" class="button icon bars">bars</a>
    <a href="#button" class="button icon bars_alt">bars_alt</a>
    <a href="#button" class="button icon battery_charging">battery_charging</a>
    <a href="#button" class="button icon battery_empty">battery_empty</a>
    <a href="#button" class="button icon battery_full">battery_full</a>
    <a href="#button" class="button icon battery_half">battery_half</a>
    <a href="#button" class="button icon beaker_alt1">beaker_alt1</a>
    <a href="#button" class="button icon beaker_alt2">beaker_alt2</a>
    <a href="#button" class="button icon bolt">bolt</a>
    <a href="#button" class="button icon book">book</a>
    <a href="#button" class="button icon book_alt">book_alt</a>
    <a href="#button" class="button icon book_alt2">book_alt2</a>
    <a href="#button" class="button icon box">box</a>
    <a href="#button" class="button icon brush">brush</a>
    <a href="#button" class="button icon brush_alt">brush_alt</a>
    <a href="#button" class="button icon calendar">calendar</a>
    <a href="#button" class="button icon calendar_alt_fill">calendar_alt_fill</a>
    <a href="#button" class="button icon calendar_alt_stroke">calendar_alt_stroke</a>
    <a href="#button" class="button icon camera">camera</a>
    <a href="#button" class="button icon cd">cd</a>
    <a href="#button" class="button icon chart">chart</a>
    <a href="#button" class="button icon chart_alt">chart_alt</a>
    <a href="#button" class="button icon chat">chat</a>
    <a href="#button" class="button icon chat_alt_fill">chat_alt_fill</a>
    <a href="#button" class="button icon chat_alt_stroke">chat_alt_stroke</a>
    <a href="#button" class="button icon check">check</a>
    <a href="#button" class="button icon check_alt">check_alt</a>
    <a href="#button" class="button icon clock">clock</a>
    <a href="#button" class="button icon cloud">cloud</a>
    <a href="#button" class="button icon cloud_download">cloud_download</a>
    <a href="#button" class="button icon cloud_upload">cloud_upload</a>
    <a href="#button" class="button icon cog">cog</a>
    <a href="#button" class="button icon comment_alt1_fill">comment_alt1_fill</a>
    <a href="#button" class="button icon comment_alt1_stroke">comment_alt1_stroke</a>
    <a href="#button" class="button icon comment_alt2_fill">comment_alt2_fill</a>
    <a href="#button" class="button icon comment_alt2_stroke">comment_alt2_stroke</a>
    <a href="#button" class="button icon comment_fill">comment_fill</a>
    <a href="#button" class="button icon comment_stroke">comment_stroke</a>
    <a href="#button" class="button icon compass">compass</a>
    <a href="#button" class="button icon cursor">cursor</a>
    <a href="#button" class="button icon curved_arrow">curved_arrow</a>
    <a href="#button" class="button icon denied">denied</a>
    <a href="#button" class="button icon dial">dial</a>
    <a href="#button" class="button icon document_alt_fill">document_alt_fill</a>
    <a href="#button" class="button icon document_alt_stroke">document_alt_stroke</a>
    <a href="#button" class="button icon document_fill">document_fill</a>
    <a href="#button" class="button icon document_stroke">document_stroke</a>
    <a href="#button" class="button icon download">download</a>
    <a href="#button" class="button icon eject">eject</a>
    <a href="#button" class="button icon equalizer">equalizer</a>
    <a href="#button" class="button icon eye">eye</a>
    <a href="#button" class="button icon eyedropper">eyedropper</a>
    <a href="#button" class="button icon first">first</a>
    <a href="#button" class="button icon folder_fill">folder_fill</a>
    <a href="#button" class="button icon folder_stroke">folder_stroke</a>
    <a href="#button" class="button icon fork">fork</a>
    <a href="#button" class="button icon fullscreen">fullscreen</a>
    <a href="#button" class="button icon fullscreen_alt">fullscreen_alt</a>
    <a href="#button" class="button icon fullscreen_exit">fullscreen_exit</a>
    <a href="#button" class="button icon fullscreen_exit_alt">fullscreen_exit_alt</a>
    <a href="#button" class="button icon hash">hash</a>
    <a href="#button" class="button icon headphones">headphones</a>
    <a href="#button" class="button icon heart_fill">heart_fill</a>
    <a href="#button" class="button icon heart_stroke">heart_stroke</a>
    <a href="#button" class="button icon home">home</a>
    <a href="#button" class="button icon image">image</a>
    <a href="#button" class="button icon info_alt1">info_alt1</a>
    <a href="#button" class="button icon iphone">iphone</a>
    <a href="#button" class="button icon key_fill">key_fill</a>
    <a href="#button" class="button icon key_stroke">key_stroke</a>
    <a href="#button" class="button icon last">last</a>
    <a href="#button" class="button icon layers">layers</a>
    <a href="#button" class="button icon layers_alt">layers_alt</a>
    <a href="#button" class="button icon left_quote">left_quote</a>
    <a href="#button" class="button icon left_quote_alt">left_quote_alt</a>
    <a href="#button" class="button icon lightbulb">lightbulb</a>
    <a href="#button" class="button icon link">link</a>
    <a href="#button" class="button icon list">list</a>
    <a href="#button" class="button icon list_nested">list_nested</a>
    <a href="#button" class="button icon lock_fill">lock_fill</a>
    <a href="#button" class="button icon lock_stroke">lock_stroke</a>
    <a href="#button" class="button icon loop">loop</a>
    <a href="#button" class="button icon loop_alt1">loop_alt1</a>
    <a href="#button" class="button icon loop_alt2">loop_alt2</a>
    <a href="#button" class="button icon loop_alt3">loop_alt3</a>
    <a href="#button" class="button icon loop_alt4">loop_alt4</a>
    <a href="#button" class="button icon magnifying_glass">magnifying_glass</a>
    <a href="#button" class="button icon mail">mail</a>
    <a href="#button" class="button icon map_pin_alt1">map_pin_alt1</a>
    <a href="#button" class="button icon map_pin_fill">map_pin_fill</a>
    <a href="#button" class="button icon map_pin_stroke">map_pin_stroke</a>
    <a href="#button" class="button icon mic">mic</a>
    <a href="#button" class="button icon minus">minus</a>
    <a href="#button" class="button icon minus_alt">minus_alt</a>
    <a href="#button" class="button icon moon_fill">moon_fill</a>
    <a href="#button" class="button icon moon_stroke">moon_stroke</a>
    <a href="#button" class="button icon move">move</a>
    <a href="#button" class="button icon move_alt1">move_alt1</a>
    <a href="#button" class="button icon move_alt2">move_alt2</a>
    <a href="#button" class="button icon move_horizontal">move_horizontal</a>
    <a href="#button" class="button icon move_horizontal_alt1">move_horizontal_alt1</a>
    <a href="#button" class="button icon move_horizontal_alt2">move_horizontal_alt2</a>
    <a href="#button" class="button icon move_vertical">move_vertical</a>
    <a href="#button" class="button icon move_vertical_alt1">move_vertical_alt1</a>
    <a href="#button" class="button icon move_vertical_alt2">move_vertical_alt2</a>
    <a href="#button" class="button icon movie">movie</a>
    <a href="#button" class="button icon new_window">new_window</a>
    <a href="#button" class="button icon pause">pause</a>
    <a href="#button" class="button icon pen">pen</a>
    <a href="#button" class="button icon pen_alt2">pen_alt2</a>
    <a href="#button" class="button icon pen_alt_fill">pen_alt_fill</a>
    <a href="#button" class="button icon pen_alt_stroke">pen_alt_stroke</a>
    <a href="#button" class="button icon pilcrow">pilcrow</a>
    <a href="#button" class="button icon pin">pin</a>
    <a href="#button" class="button icon play">play</a>
    <a href="#button" class="button icon play_alt">play_alt</a>
    <a href="#button" class="button icon plus">plus</a>
    <a href="#button" class="button icon plus_alt">plus_alt</a>
    <a href="#button" class="button icon question_mark_alt1">question_mark_alt1</a>
    <a href="#button" class="button icon rain">rain</a>
    <a href="#button" class="button icon read_more">read_more</a>
    <a href="#button" class="button icon reload">reload</a>
    <a href="#button" class="button icon reload_alt">reload_alt</a>
    <a href="#button" class="button icon right_quote">right_quote</a>
    <a href="#button" class="button icon right_quote_alt">right_quote_alt</a>
    <a href="#button" class="button icon rss">rss</a>
    <a href="#button" class="button icon rss_alt">rss_alt</a>
    <a href="#button" class="button icon share">share</a>
    <a href="#button" class="button icon spin">spin</a>
    <a href="#button" class="button icon spin_alt">spin_alt</a>
    <a href="#button" class="button icon star">star</a>
    <a href="#button" class="button icon steering_wheel">steering_wheel</a>
    <a href="#button" class="button icon stop">stop</a>
    <a href="#button" class="button icon sun_fill">sun_fill</a>
    <a href="#button" class="button icon sun_stroke">sun_stroke</a>
    <a href="#button" class="button icon tag_fill">tag_fill</a>
    <a href="#button" class="button icon tag_stroke">tag_stroke</a>
    <a href="#button" class="button icon target">target</a>
    <a href="#button" class="button icon transfer">transfer</a>
    <a href="#button" class="button icon trash_fill">trash_fill</a>
    <a href="#button" class="button icon trash_stroke">trash_stroke</a>
    <a href="#button" class="button icon umbrella">umbrella</a>
    <a href="#button" class="button icon undo">undo</a>
    <a href="#button" class="button icon unlock_fill">unlock_fill</a>
    <a href="#button" class="button icon unlock_stroke">unlock_stroke</a>
    <a href="#button" class="button icon upload">upload</a>
    <a href="#button" class="button icon user">user</a>
    <a href="#button" class="button icon volume">volume</a>
    <a href="#button" class="button icon volume_mute">volume_mute</a>
    <a href="#button" class="button icon wrench">wrench</a>
    <a href="#button" class="button icon x">x</a>
    <a href="#button" class="button icon x_alt">x_alt</a>



## Browser compatibility ##

Firefox 3.5+, Google Chrome, Safari 4+, IE 8+, Opera 10+.

Note: Some CSS3 features are not supported in older versions of Opera and versions of Internet Explorer prior to IE 8. The use of icons is not supported in IE 6 or IE 7.

## License ##

Public domain: [http://unlicense.org](http://unlicense.org)

## Acknowledgements ##

Inspired by [Michael Henriksen](http://michaelhenriksen.dk)'s [CSS3 Buttons](http://github.com/michenriksen/css3buttons). Icons from [Iconic pack](http://somerandomdude.com/projects/iconic/).

Forked from [necolas] (http://github.com/necolas/css3-github-buttons)