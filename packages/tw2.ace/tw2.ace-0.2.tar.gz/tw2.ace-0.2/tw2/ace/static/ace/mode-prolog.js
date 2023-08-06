/* ***** BEGIN LICENSE BLOCK *****
 * Distributed under the BSD license:
 *
 * Copyright (c) 2012, Ajax.org B.V.
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of Ajax.org B.V. nor the
 *       names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL AJAX.ORG B.V. BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *
 * Contributor(s):
 * 
 *
 *
 * ***** END LICENSE BLOCK ***** */

ace.define('ace/mode/prolog', ['require', 'exports', 'module' , 'ace/lib/oop', 'ace/mode/text', 'ace/tokenizer', 'ace/mode/prolog_highlight_rules', 'ace/mode/folding/cstyle'], function(require, exports, module) {


var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var Tokenizer = require("../tokenizer").Tokenizer;
var PrologHighlightRules = require("./prolog_highlight_rules").PrologHighlightRules;
var FoldMode = require("./folding/cstyle").FoldMode;

var Mode = function() {
    var highlighter = new PrologHighlightRules();
    this.foldingRules = new FoldMode();
    this.$tokenizer = new Tokenizer(highlighter.getRules());
};
oop.inherits(Mode, TextMode);

(function() {
}).call(Mode.prototype);

exports.Mode = Mode;
});

ace.define('ace/mode/prolog_highlight_rules', ['require', 'exports', 'module' , 'ace/lib/oop', 'ace/mode/text_highlight_rules'], function(require, exports, module) {


var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

var PrologHighlightRules = function() {

    this.$rules = 
        {
    "start": [
        {
            "token": [
                "#comments"
            ],
            "regex": ""
        },
        {
            "token": [
                {
                    "1": {
                        "name": "keyword.control.clause.bodybegin.prolog"
                    }
                },
                "meta.clause.body.prolog"
            ],
            "regex": "(?<=\\))\\s*(:-)", // ERROR: This contains a lookbehind, which JS does not support :(",
            "next": "state_2"
        },
        {
            "token": [
                {
                    "1": {
                        "name": "entity.name.function.clause.headbegin.prolog"
                    }
                },
                "meta.clause.head.prolog"
            ],
            "regex": "^\\s*([a-zA-Z][a-zA-Z0-9_]*\\()(?=.*:-.*)",
            "next": "state_3"
        },
        {
            "token": [
                {
                    "1": {
                        "name": "entity.name.function.dcg.headbegin.prolog"
                    }
                },
                "meta.dcg.head.prolog"
            ],
            "regex": "^\\s*([a-z][a-zA-Z0-9_]*\\()(?=.*-->.*)",
            "next": "state_4"
        },
        {
            "token": [
                {
                    "1": {
                        "name": "keyword.control.dcg.bodybegin.prolog"
                    }
                },
                "meta.dcg.body.prolog"
            ],
            "regex": "(?<=\\))\\s*(-->)", // ERROR: This contains a lookbehind, which JS does not support :(",
            "next": "state_5"
        },
        {
            "token": [
                "entity.name.function.fact.prolog",
                "entity.name.function.fact.prolog"
            ],
            "regex": "\\s*[a-zA-Z][a-zA-Z0-9_]*\\([^\\.]*\\)[\\s^\\n]*\\."
        }
    ],
    "state_2": [
        {
            "include": "#comments"
        },
        {
            "include": "#builtin"
        },
        {
            "include": "#controlandkeywords"
        },
        {
            "include": "#atom"
        },
        {
            "include": "#variable"
        },
        {
            "include": "#constants"
        },
        {
            "token": "meta.clause.body.prolog",
            "regex": "."
        },
        {
            "token": "TODO",
            "regex": "[.^%]*(\\.)",
            "next": "start"
        }
    ],
    "state_3": [
        {
            "include": "#atom"
        },
        {
            "include": "#variable"
        },
        {
            "include": "#constants"
        },
        {
            "token": "TODO",
            "regex": "(\\))(?=\\s*:-)",
            "next": "start"
        }
    ],
    "state_4": [
        {
            "include": "#atom"
        },
        {
            "include": "#variable"
        },
        {
            "include": "#constants"
        },
        {
            "token": "TODO",
            "regex": "(\\))(?=\\s*-->)",
            "next": "start"
        }
    ],
    "state_5": [
        {
            "include": "#comments"
        },
        {
            "include": "#controlandkeywords"
        },
        {
            "include": "#atom"
        },
        {
            "include": "#variable"
        },
        {
            "include": "#constants"
        },
        {
            "token": "meta.dcg.body.prolog",
            "regex": "."
        },
        {
            "token": "TODO",
            "regex": "[.^%]*(\\.)",
            "next": "start"
        }
    ]
}
};

oop.inherits(PrologHighlightRules, TextHighlightRules);

exports.PrologHighlightRules = PrologHighlightRules;
});

ace.define('ace/mode/folding/cstyle', ['require', 'exports', 'module' , 'ace/lib/oop', 'ace/range', 'ace/mode/folding/fold_mode'], function(require, exports, module) {


var oop = require("../../lib/oop");
var Range = require("../../range").Range;
var BaseFoldMode = require("./fold_mode").FoldMode;

var FoldMode = exports.FoldMode = function() {};
oop.inherits(FoldMode, BaseFoldMode);

(function() {

    this.foldingStartMarker = /(\{|\[)[^\}\]]*$|^\s*(\/\*)/;
    this.foldingStopMarker = /^[^\[\{]*(\}|\])|^[\s\*]*(\*\/)/;

    this.getFoldWidgetRange = function(session, foldStyle, row) {
        var line = session.getLine(row);
        var match = line.match(this.foldingStartMarker);
        if (match) {
            var i = match.index;

            if (match[1])
                return this.openingBracketBlock(session, match[1], row, i);

            return session.getCommentFoldRange(row, i + match[0].length, 1);
        }

        if (foldStyle !== "markbeginend")
            return;

        var match = line.match(this.foldingStopMarker);
        if (match) {
            var i = match.index + match[0].length;

            if (match[1])
                return this.closingBracketBlock(session, match[1], row, i);

            return session.getCommentFoldRange(row, i, -1);
        }
    };

}).call(FoldMode.prototype);

});
