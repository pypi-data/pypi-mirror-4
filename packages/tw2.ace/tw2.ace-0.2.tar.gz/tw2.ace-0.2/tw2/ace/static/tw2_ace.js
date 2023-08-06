// Globals
var ace_textarea = ace.require("ace/ext/textarea");
ace_textarea.editors = {};

function tw2_ace(target, theme, mode, options) {
	// var editor = ace.edit(target);
	var editor;
	if (options && options.settings_panel) {
		editor = ace_textarea.transformTextarea(
				document.getElementById(target), options.settings_panel);
	} else {
		editor = ace_textarea.transformTextarea(
				document.getElementById(target), false);
	}
	var session = editor.getSession();

	if (theme) {
		editor.setTheme("ace/theme/" + theme);
	}
	;
	if (mode) {
		session.setMode("ace/mode/" + mode);
	}
	;

	if (options) {
		editor.renderer.setShowGutter(options.show_gutter);
		if (Boolean(options.soft_wrap)) {
			session.setUseWrapMode(true);
			var col = parseInt(options.soft_wrap, 10);
			if (isNaN(col))
				col = null;
			session.setWrapLimitRange(col, col);
		} else {
			session.setUseWrapMode(false);
		}

		if (options.clone_pre_style) {
			// Create a hidden dummy pre element and clone the styles
			var p = document.createElement("pre");
			p.style.visibility = "hidden";
			p = document.body.appendChild(p);
			var s = window.getComputedStyle(p);
			editor.container.style.fontSize = s.fontSize;
			editor.container.style.fontFamily = s.fontFamily;
			document.body.removeChild(p);
			delete p;
		}
	}

	ace_textarea.editors[target] = editor;
	return editor;
}
