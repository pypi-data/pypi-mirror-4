" Vim syntax file
" Language:	templ
" Maintainer:	Brian Mearns <Brian.Mearns@apcc.com>
" Last Change:	2012 Aug 05

" For version 5.x: Clear all syntax items
" For version 6.x: Quit when a syntax file was already loaded
if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

syn sync fromstart
syn case match

" Nested syntax.
" matchgroup is what's used for the text that matches the "start" and "end"
" patterns, not the stuff in betwee. That's what "Snip" is for.
hi link Snip SpecialComment

"Vimtip #857
" Adds a nested syntax region which is highlighted as though syntax is
" "filetype". Region is bound by patterns "start" and "end", and "textSnipHl"
" is the highlight class to use for highlighting the actual start and end tags
" (not the stuff inbetween them, that's highlighted using the specified
" syntax.)
function! TextEnableCodeSnip(filetype,start,end,textSnipHl) abort
  let ft=toupper(a:filetype)
  let group='textGroup'.ft
  if exists('b:current_syntax')
    let s:current_syntax=b:current_syntax
    " Remove current syntax definition, as some syntax files (e.g. cpp.vim)
    " do nothing if b:current_syntax is defined.
    unlet b:current_syntax
  endif
  execute 'syntax include @'.group.' syntax/'.a:filetype.'.vim'
  try
    execute 'syntax include @'.group.' after/syntax/'.a:filetype.'.vim'
  catch
  endtry
  if exists('s:current_syntax')
    let b:current_syntax=s:current_syntax
  else
    unlet b:current_syntax
  endif
  execute 'syntax region textSnip'.ft.'
  \ matchgroup='.a:textSnipHl.'
  \ start="'.a:start.'" end="'.a:end.'"
  \ contains=@'.group
endfunction

function! AddKnownFunction(tag)
    execute 'syntax match templKnownFunctions contained containedin=templTag /' . a:tag . '\(\_\s\|}\)/'
endfunction

"This is special purpose nested for templ.
" use a "don't" comment and then "syntax LANG" specifying the appropriate
" LANG. It can be spread out across arbitrary whitespace and lines, and can 
" even include a % comment at the end (but not in between).
function! TemplCodeSnip(filetyp,)
        call TextEnableCodeSnip(a:filetyp,
                \ '{\_\s*\(dont\_\s\+\)\?syntax\_\s\+'.a:filetyp.'\_\s*\(%.*\_$\)*\_\s*}',
                \ '{\_\s*\(dont\_\s\+\)\?end-syntax\_\s\+'.a:filetyp.'\_\s*\(%.*\_$\)*\_\s*}',
                \ 'SpecialComment')
endfunction
call TemplCodeSnip("c")
call TemplCodeSnip("cpp")
call TemplCodeSnip("java")
call TemplCodeSnip("python")
call TemplCodeSnip("xml")
call TemplCodeSnip("html")
call TemplCodeSnip("javascript")
call TemplCodeSnip("css")

" Tags inside comments
syn     match       templDocTagTodo        "TODO\c"                    contained
syn     match       templDocTagFixme       "FIXME\c"                   contained
syn     match       templDocTagXXX         "XXX"                       contained
syn     match       templDocTagWarning     "WARN:\c"he=e-1             contained
syn     match       templDocTagError       "ERROR:\c"he=e-1            contained
syn     match       templDocTagCust        "![^:]*:"hs=s+1,he=e-1      contained
syn cluster templDocTag contains=templDocTag.*

"basically any templCode.
syn cluster templCode contains=templList,MLineComment,templTag,templEOLComment,templStringLiteral,templEmbedded

"A templ list. Just bounded by { } unless escaped. It can contain any
"additional templcode.
syn region templList matchgroup=Delimiter start="\(^\|[^\\]\){"hs=s+1 matchgroup=Delimiter end="}" contains=@templCode

"An embedded template. Contained in a templList, contains anything the top can
"contain (TOP) except string literals (they can be contained in templLists inside the embed).
syn region templEmbedded matchgroup=Operator start='<<<' end='>>>' contained containedin=templList contains=TOP,templStringLiteral

"Multiline comment is a "dont" command, which has to contain well formed but
"not valid templ code. Except we just call it "commentedCode" so it doesn't
"get highlighted as though it's working code.
syn region MLineComment	matchgroup=CommentDelimiter start="\(^\|[^\\]\){\_\s*dont\_\s\+" end="}" extend fold contains=commentedCode,@templDocTag
syn region MLineComment	matchgroup=CommentDelimiter start="\(^\|[^\\]\){\_\s*rem\_\s\+" end="}" extend fold contains=commentedCode,@templDocTag
syn region MLineComment	matchgroup=CommentDelimiter start="\(^\|[^\\]\){\_\s*\#\_\s\+" end="}" extend fold contains=commentedCode,@templDocTag
syn region MLineComment	matchgroup=CommentDelimiter start="\(^\|[^\\]\){\_\s*syn\_\s\+" end="}" extend fold contains=commentedCode,@templDocTag
syn region MLineComment	matchgroup=CommentDelimiter start="\(^\|[^\\]\){\_\s*syntax\_\s\+" end="}" extend fold contains=commentedCode,@templDocTag
syn region MLineComment	matchgroup=CommentDelimiter start="\(^\|[^\\]\){\_\s*end-syn\_\s\+" end="}" extend fold contains=commentedCode,@templDocTag
syn region MLineComment	matchgroup=CommentDelimiter start="\(^\|[^\\]\){\_\s*end-syntax\_\s\+" end="}" extend fold contains=commentedCode,@templDocTag

syn region commentedCode contained start="\(^\|[^\\]\){" skip='/"[^"]*"/' end="}"	contains=commentedCode

"an end of line comment.
syn match templEOLComment "%.*" contained containedin=templList

"String literals. I stole this from c.vim.
syn region templStringLiteral start=+"+ skip=+\\\\\|\\"+ end=+"+ containedin=templList

"The first symbol in a templList, except string lits. Doesn't work if the
"curly brace and tag are on separate lines, not sure why.
syn match templTag '{\@<=\_\s*[^{ \t\n\r"}]\+' contained containedin=templList contains=templKnownFunctions

"Keywords can include any printable characters except space and curly braces.
set iskeyword=33-122,124,126

call AddKnownFunction( "!=" )
call AddKnownFunction( "!==" )
call AddKnownFunction( "\\$" )
call AddKnownFunction( "\\$\\$" )
call AddKnownFunction( "\\$=" )
call AddKnownFunction( "#" )
call AddKnownFunction( "&&" )
call AddKnownFunction( "'" )
call AddKnownFunction( "\\*" )
call AddKnownFunction( "\\*\\*" )
call AddKnownFunction( "+" )
call AddKnownFunction( ",=" )
call AddKnownFunction( "\\-" )
call AddKnownFunction( ":" )
call AddKnownFunction( "::" )
call AddKnownFunction( "<" )
call AddKnownFunction( "<=" )
call AddKnownFunction( "==" )
call AddKnownFunction( "===" )
call AddKnownFunction( ">" )
call AddKnownFunction( ">\\*<" )
call AddKnownFunction( "><" )
call AddKnownFunction( ">=" )
call AddKnownFunction( "?" )
call AddKnownFunction( "@" )
syn keyword templKnownFunctions contained containedin=templTag
    \ acos
    \ add
    \ aliases
    \ all
    \ and
    \ any
    \ append
    \ arc-cosine
    \ arc-sine
    \ arc-tangent
    \ arc-tangent-quad
    \ asin
    \ at
    \ atan
    \ atan-quad
    \ atanq
    \ block
    \ bool
    \ bool.f
    \ bool.new
    \ bool.t
    \ buffer
    \ buffer-to
    \ caaar
    \ caadr
    \ caar
    \ cadar
    \ caddr
    \ cadr
    \ call
    \ car
    \ cat
    \ ccb
    \ cdaar
    \ cdadr
    \ cddar
    \ cdddr
    \ cddr
    \ cdr
    \ ceil
    \ char-at
    \ chars
    \ chr
    \ close
    \ cons
    \ cons.len
    \ cons.new
    \ cos
    \ cosine
    \ deg
    \ div
    \ div.mode
    \ divmod
    \ doc
    \ dont
    \ eccb
    \ echo
    \ embed
    \ empty
    \ end-syn
    \ end-syntax
    \ eocb
    \ eol
    \ eq
    \ equal
    \ equiv
    \ error
    \ eval
    \ exe-name
    \ exe.is
    \ exec
    \ exec-block
    \ exename
    \ exists
    \ exp
    \ exp.and
    \ exp.block
    \ exp.call
    \ exp.echo
    \ exp.join
    \ exp.let
    \ exp.or
    \ exp.scope
    \ false
    \ fields
    \ file.close
    \ file.open
    \ file.read
    \ file.write
    \ filepos
    \ filepos-plist
    \ filepos-tuple
    \ find
    \ first
    \ first-of-first
    \ first-of-first-of-first
    \ first-of-first-of-rest
    \ first-of-rest
    \ first-of-rest-of-first
    \ first-of-rest-of-rest
    \ flatten
    \ floor
    \ for
    \ for.gen
    \ for.loop
    \ gen
    \ gen-loop
    \ gen-while
    \ get
    \ getf
    \ getset
    \ glue
    \ gmtime
    \ gt
    \ gte
    \ hasf
    \ idxf
    \ if
    \ imp
    \ implode
    \ in
    \ in-str
    \ include
    \ include-as-list
    \ insert
    \ invoke
    \ is-empty
    \ is-exe
    \ is-false
    \ is-list
    \ is-null
    \ is-str
    \ is-true
    \ join
    \ lambda
    \ len
    \ let
    \ list
    \ list.append
    \ list.at
    \ list.cat
    \ list.empty
    \ list.filepos
    \ list.find
    \ list.flatten
    \ list.has
    \ list.in
    \ list.insert
    \ list.is
    \ list.len
    \ list.new
    \ list.nil
    \ list.reverse
    \ list.slice
    \ list.sort
    \ list.splice
    \ list.version
    \ ln
    \ lnbrk
    \ localtime
    \ log
    \ loop
    \ loop.gen
    \ loop.loop
    \ lt
    \ lte
    \ math.add
    \ math.div
    \ math.divmod
    \ math.e
    \ math.exp
    \ math.mult
    \ math.neg
    \ math.pow
    \ math.sub
    \ mod
    \ mt
    \ mult
    \ neg
    \ neq
    \ nequiv
    \ nil
    \ not
    \ not-equal
    \ null.is
    \ ocb
    \ open
    \ or
    \ ord
    \ ord-1
    \ pck.block
    \ pck.call
    \ pck.echo
    \ pck.join
    \ pck.let
    \ pck.scope
    \ pi
    \ pipe
    \ pipe-both
    \ plist.fields
    \ plist.filepos
    \ plist.find
    \ plist.get
    \ plist.idx
    \ plist.in
    \ plist.len
    \ plist.version
    \ pow
    \ rad
    \ rand
    \ rand-float
    \ randint
    \ random.float
    \ random.int
    \ range
    \ read
    \ redirect
    \ rem
    \ rest
    \ rest-of-first-of-first
    \ rest-of-first-of-rest
    \ rest-of-rest
    \ rest-of-rest-of-first
    \ rest-of-rest-of-rest
    \ return
    \ reverse
    \ round
    \ scope
    \ set
    \ sin
    \ sine
    \ slice
    \ sort
    \ spit
    \ splice
    \ sqrt
    \ stamp
    \ stderr
    \ stdin
    \ stdout
    \ str
    \ str.at
    \ str.cat
    \ str.filepos
    \ str.find
    \ str.in
    \ str.is
    \ str.len
    \ str.list
    \ str.lower
    \ str.new
    \ str.reverse
    \ str.slice
    \ str.upper
    \ str.version
    \ strlen
    \ strpos
    \ sub
    \ substr
    \ syn
    \ syntax
    \ system
    \ tab
    \ tan
    \ tangent
    \ tau
    \ time
    \ time-plist
    \ time.stamp
    \ time.time
    \ time.toPlist
    \ time.utctime
    \ to-lower
    \ to-upper
    \ true
    \ try
    \ unpack
    \ unret
    \ utctime
    \ v
    \ value-of-the-argument
    \ vars
    \ version
    \ version-plist
    \ version-tuple
    \ void
    \ vota
    \ while
    \ while.gen
    \ while.loop
    \ write
    \ xor


"Highlighting.
hi      link    templList               Special
hi      link    templTag                Statement
hi      link    templKnownFunctions     Function
hi      link    MLineComment            Comment
hi      link    templEOLComment         Comment
hi      link    commentedCode           Comment
hi      link    CommentDelimiter        SpecialComment
hi      link    templStringLiteral      String
hi      link    templDocTag             Todo
hi      link    templDocTagTodo         templDocTag
hi      link    templDocTagFixme        templDocTag
hi      link    templDocTagXXX          templDocTag
hi      link    templDocTagCust         templDocTag
hi      link    templDocTagError        error
hi      link    templDocTagWarning      templDocTag


let b:current_syntax = "templ"

