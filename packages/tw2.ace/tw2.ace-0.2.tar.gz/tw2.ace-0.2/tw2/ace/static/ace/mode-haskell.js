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

ace.define('ace/mode/haskell', ['require', 'exports', 'module' , 'ace/lib/oop', 'ace/mode/text', 'ace/tokenizer', 'ace/mode/haskell_highlight_rules', 'ace/mode/folding/cstyle'], function(require, exports, module) {


var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var Tokenizer = require("../tokenizer").Tokenizer;
var HaskellHighlightRules = require("./haskell_highlight_rules").HaskellHighlightRules;
var FoldMode = require("./folding/cstyle").FoldMode;

var Mode = function() {
    var highlighter = new HaskellHighlightRules();
    this.foldingRules = new FoldMode();
    this.$tokenizer = new Tokenizer(highlighter.getRules());
};
oop.inherits(Mode, TextMode);

(function() {
}).call(Mode.prototype);

exports.Mode = Mode;
});

ace.define('ace/mode/haskell_highlight_rules', ['require', 'exports', 'module' , 'ace/lib/oop', 'ace/mode/text_highlight_rules'], function(require, exports, module) {


var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

var HaskellHighlightRules = function() {

    this.$rules = 
        {
    "start": [
        {
            "token": [
                [],
                {
                    "1": {
                        "name": "punctuation.definition.entity.haskell"
                    },
                    "2": {
                        "name": "punctuation.definition.entity.haskell"
                    }
                },
                "keyword.operator.function.infix.haskell"
            ],
            "regex": "(`)[a-zA-Z_']*?(`)"
        },
        {
            "token": [
                "constant.language.unit.haskell",
                "constant.language.unit.haskell"
            ],
            "regex": "\\(\\)"
        },
        {
            "token": [
                "constant.language.empty-list.haskell",
                "constant.language.empty-list.haskell"
            ],
            "regex": "\\[\\]"
        },
        {
            "token": [
                {
                    "1": {
                        "name": "keyword.other.haskell"
                    }
                },
                "meta.declaration.module.haskell"
            ],
            "regex": "(module)",
            "next": "state_4"
        },
        {
            "token": [
                {
                    "1": {
                        "name": "keyword.other.haskell"
                    }
                },
                "meta.declaration.class.haskell"
            ],
            "regex": "\\b(class)\\b",
            "next": "state_5"
        },
        {
            "token": [
                {
                    "1": {
                        "name": "keyword.other.haskell"
                    }
                },
                "meta.declaration.instance.haskell"
            ],
            "regex": "\\b(instance)\\b",
            "next": "state_6"
        },
        {
            "token": [
                {
                    "1": {
                        "name": "keyword.other.haskell"
                    }
                },
                "meta.import.haskell"
            ],
            "regex": "(import)",
            "next": "state_7"
        },
        {
            "token": [
                {
                    "1": {
                        "name": "keyword.other.haskell"
                    }
                },
                "meta.deriving.haskell"
            ],
            "regex": "(deriving)\\s*\\(",
            "next": "state_8"
        },
        {
            "token": [
                "keyword.other.haskell",
                "keyword.other.haskell"
            ],
            "regex": "\\b(deriving|where|data|type|case|of|let|in|newtype|default)\\b"
        },
        {
            "token": [
                "keyword.operator.haskell",
                "keyword.operator.haskell"
            ],
            "regex": "\\binfix[lr]?\\b"
        },
        {
            "token": [
                "keyword.control.haskell",
                "keyword.control.haskell"
            ],
            "regex": "\\b(do|if|then|else)\\b"
        },
        {
            "token": [
                "constant.numeric.float.haskell",
                "constant.numeric.float.haskell"
            ],
            "regex": "\\b([0-9]+\\.[0-9]+([eE][+-]?[0-9]+)?|[0-9]+[eE][+-]?[0-9]+)\\b"
        },
        {
            "token": [
                "constant.numeric.haskell",
                "constant.numeric.haskell"
            ],
            "regex": "\\b([0-9]+|0([xX][0-9a-fA-F]+|[oO][0-7]+))\\b"
        },
        {
            "token": [
                [],
                {
                    "1": {
                        "name": "punctuation.definition.preprocessor.c"
                    }
                },
                "meta.preprocessor.c"
            ],
            "regex": "^\\s*(#)\\s*\\w+"
        },
        {
            "token": [
                "#pragma"
            ],
            "regex": ""
        },
        {
            "token": [
                {
                    "0": {
                        "name": "punctuation.definition.string.begin.haskell"
                    }
                },
                "string.quoted.double.haskell"
            ],
            "regex": "\"",
            "next": "state_16"
        },
        {
            "token": [
                [],
                {
                    "1": {
                        "name": "punctuation.definition.string.begin.haskell"
                    },
                    "2": {
                        "name": "constant.character.escape.haskell"
                    },
                    "3": {
                        "name": "constant.character.escape.octal.haskell"
                    },
                    "4": {
                        "name": "constant.character.escape.hexadecimal.haskell"
                    },
                    "5": {
                        "name": "constant.character.escape.control.haskell"
                    },
                    "6": {
                        "name": "punctuation.definition.string.end.haskell"
                    }
                },
                "string.quoted.single.haskell"
            ],
            "regex": "(?x)(')(?:[\\ -\\[\\]-~]|(\\\\(?:NUL|SOH|STX|ETX|EOT|ENQ|ACK|BEL|BS|HT|LF|VT|FF|CR|SO|SI|DLE|DC1|DC2|DC3|DC4|NAK|SYN|ETB|CAN|EM|SUB|ESC|FS|GS|RS|US|SP|DEL|[abfnrtv\\\\\\\"'\\&]))|(\\\\o[0-7]+)|(\\\\x[0-9A-Fa-f]+)|(\\^[A-Z@\\[\\]\\\\\\^_]))(')"
        },
        {
            "token": [
                {
                    "1": {
                        "name": "entity.name.function.haskell"
                    },
                    "2": {
                        "name": "keyword.other.double-colon.haskell"
                    }
                },
                "meta.function.type-declaration.haskell"
            ],
            "regex": "^\\s*([a-z_][a-zA-Z0-9_']*|\\([|!%$+\\-.,=</>]+\\))\\s*(::)",
            "next": "state_18"
        },
        {
            "token": [
                "support.constant.haskell",
                "support.constant.haskell"
            ],
            "regex": "\\b(Just|Nothing|Left|Right|True|False|LT|EQ|GT|\\(\\)|\\[\\])\\b"
        },
        {
            "token": [
                "constant.other.haskell",
                "constant.other.haskell"
            ],
            "regex": "\\b[A-Z]\\w*\\b"
        },
        {
            "token": [
                "#comments"
            ],
            "regex": ""
        },
        {
            "token": [
                "support.function.prelude.haskell",
                "support.function.prelude.haskell"
            ],
            "regex": "\\b(abs|acos|acosh|all|and|any|appendFile|applyM|asTypeOf|asin|asinh|atan|atan2|atanh|break|catch|ceiling|compare|concat|concatMap|const|cos|cosh|curry|cycle|decodeFloat|div|divMod|drop|dropWhile|elem|encodeFloat|enumFrom|enumFromThen|enumFromThenTo|enumFromTo|error|even|exp|exponent|fail|filter|flip|floatDigits|floatRadix|floatRange|floor|fmap|foldl|foldl1|foldr|foldr1|fromEnum|fromInteger|fromIntegral|fromRational|fst|gcd|getChar|getContents|getLine|head|id|init|interact|ioError|isDenormalized|isIEEE|isInfinite|isNaN|isNegativeZero|iterate|last|lcm|length|lex|lines|log|logBase|lookup|map|mapM|mapM_|max|maxBound|maximum|maybe|min|minBound|minimum|mod|negate|not|notElem|null|odd|or|otherwise|pi|pred|print|product|properFraction|putChar|putStr|putStrLn|quot|quotRem|read|readFile|readIO|readList|readLn|readParen|reads|readsPrec|realToFrac|recip|rem|repeat|replicate|return|reverse|round|scaleFloat|scanl|scanl1|scanr|scanr1|seq|sequence|sequence_|show|showChar|showList|showParen|showString|shows|showsPrec|significand|signum|sin|sinh|snd|span|splitAt|sqrt|subtract|succ|sum|tail|take|takeWhile|tan|tanh|toEnum|toInteger|toRational|truncate|uncurry|undefined|unlines|until|unwords|unzip|unzip3|userError|words|writeFile|zip|zip3|zipWith|zipWith3)\\b"
        },
        {
            "token": [
                "#infix_op"
            ],
            "regex": ""
        },
        {
            "token": [
                "keyword.operator.haskell",
                "keyword.operator.haskell"
            ],
            "regex": "[|!%$?~+:\\-.=</>\\\\]+"
        },
        {
            "token": [
                "punctuation.separator.comma.haskell",
                "punctuation.separator.comma.haskell"
            ],
            "regex": ","
        }
    ],
    "state_4": [
        {
            "include": "#module_name"
        },
        {
            "include": "#module_exports"
        },
        {
            "token": "invalid",
            "regex": "[a-z]+"
        },
        {
            "token": "TODO",
            "regex": "(where)",
            "next": "start"
        }
    ],
    "state_5": [
        {
            "token": "support.class.prelude.haskell",
            "regex": "\\b(Monad|Functor|Eq|Ord|Read|Show|Num|(Frac|Ra)tional|Enum|Bounded|Real(Frac|Float)?|Integral|Floating)\\b"
        },
        {
            "token": "entity.other.inherited-class.haskell",
            "regex": "[A-Z][A-Za-z_']*"
        },
        {
            "token": "variable.other.generic-type.haskell",
            "regex": "\\b[a-z][a-zA-Z0-9_']*\\b"
        },
        {
            "token": "TODO",
            "regex": "\\b(where)\\b",
            "next": "start"
        }
    ],
    "state_6": [
        {
            "include": "#type_signature"
        },
        {
            "token": "TODO",
            "regex": "\\b(where)\\b|$",
            "next": "start"
        }
    ],
    "state_7": [
        {
            "token": "keyword.other.haskell",
            "regex": "(qualified|as|hiding)"
        },
        {
            "include": "#module_name"
        },
        {
            "include": "#module_exports"
        },
        {
            "token": "TODO",
            "regex": "($|;)",
            "next": "start"
        }
    ],
    "state_8": [
        {
            "token": "entity.other.inherited-class.haskell",
            "regex": "\\b[A-Z][a-zA-Z_']*"
        },
        {
            "token": "TODO",
            "regex": "\\)",
            "next": "start"
        }
    ],
    "state_16": [
        {
            "token": "constant.character.escape.haskell",
            "regex": "\\\\(NUL|SOH|STX|ETX|EOT|ENQ|ACK|BEL|BS|HT|LF|VT|FF|CR|SO|SI|DLE|DC1|DC2|DC3|DC4|NAK|SYN|ETB|CAN|EM|SUB|ESC|FS|GS|RS|US|SP|DEL|[abfnrtv\\\\\\\"'\\&])"
        },
        {
            "token": "constant.character.escape.octal.haskell",
            "regex": "\\\\o[0-7]+|\\\\x[0-9A-Fa-f]+|\\\\[0-9]+"
        },
        {
            "token": "constant.character.escape.control.haskell",
            "regex": "\\^[A-Z@\\[\\]\\\\\\^_]"
        },
        {
            "token": "TODO",
            "regex": "\"",
            "next": "start"
        }
    ],
    "state_18": [
        {
            "include": "#type_signature"
        },
        {
            "token": "TODO",
            "regex": "$\\n?",
            "next": "start"
        }
    ]
}
};

oop.inherits(HaskellHighlightRules, TextHighlightRules);

exports.HaskellHighlightRules = HaskellHighlightRules;
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
