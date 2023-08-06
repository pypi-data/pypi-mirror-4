
====================================
templ - Template Processing Language
====================================


.. contents:: Contents
    :depth: 2


.. _Section-1:

1: Introduction
---------------

\ **templ**\  is the \ **Tem**\ plate \ **P**\ rocessing \ **L**\ anguage. 



\ ``templ``\  is a (Turing complete) programming language, used for content generation
from text-based template files and a simple but powerful processing language
(\ ``templ``\  itself) which is embedded directly in the template file. 



\ ``templ``\  can be used for: 

- Code generation.
- Form letters.
- Server-side scripting for web servers.
- Customized markup with variant output formats.
- Any other kind of dynamic text-based content generation.



.. _Section-1.1:

1.1: Contact Information
~~~~~~~~~~~~~~~~~~~~~~~~

This project is currently hosted on `bitbucket <https://bitbucket.org>`_, 
at `https://bitbucket.org/bmearns/templ/ <https://bitbucket.org/bmearns/templ/>`_. The primary author is Brian Mearns:
you can contact Brian through bitbucket at `https://bitbucket.org/bmearns <https://bitbucket.org/bmearns>`_. 



.. _Section-1.2:

1.2: Copyright and License
~~~~~~~~~~~~~~~~~~~~~~~~~~

\ ``templ``\  is \ *free software*\ : you can redistribute it and/or modify
it under the terms of the \ **GNU Affero General Public License**\  as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. 



\ ``templ``\  is distributed in the hope that it will be useful,
but \ **without any warranty**\ ; without even the implied warranty of
\ *merchantability*\  or \ *fitness for a particular purpose*\ .  See the
GNU Affero General Public License for more details. 



A copy of the GNU Affero General Public License is available in the templ
distribution under the file LICENSE.txt. If you did not receive a copy of
this file, see `http://www.gnu.org/licenses/ <http://www.gnu.org/licenses/>`_. 



.. _Section-2:

2: Examples
-----------

The following show some simple example templates and they're output, to give
an idea of what can be done with templ.



.. _Section-2.1:

2.1: Templ Basics
~~~~~~~~~~~~~~~~~ 
            

The following template shows some of the basic elements of \ ``templ``\  templates:


            

::

    Hello, World!
    My Name is {set :NAME "templ"}. I am the TEMplate Processing Language.
    Sometimes, {$ :NAME} likes to speak in the third person.
    
    {$ :NAME} can do math:
        1 + 1 = {+ 1 1}
        1 + 2 = {+ 1 2}
        2 + 3 = {+ 2 3}
        3 + 5 = {+ 3 5}
        etc...
    
    {$ :NAME} can operate on strings and lists:
        {implode "a" {' b n n s}}
        {str {cat {' a b c } {' d e f } }}
    
    {$ :NAME} can do conditional processing:
        {if
            {== {+ 2 2} 5}
            "Oh No!"
    
            {== {+ 2 2} 4}
            "Phew!"
    
            "How did I get here?"
        }
    
    {$ :NAME} can loop (and do trig):
    {for :THETA {range 0 40 10} {
        echo "    sin(" {$ :THETA} ") = " {sin {rad {$ :THETA}}} {eol}}
    }
    
    {$ :NAME} can even do list comprehensions and user defined functions:
    {v {set
        :MY-FUNC
        {lambda
            {' :THETA }
            {:
                {let :RADS}
                {$ :RADS {rad {$ :THETA}}}
    
                {echo "Processing theta=" {$ :THETA} "..." {eol}}
    
                %return value
                {+ {cos {$ :RADS}} {sin {$ :RADS}} }
            }
        }
    }}{wrap "{" "}" {implode {glue "," {eol} "    "} {gen
        :T
        {range 40 80 10}
        {join ":" {$ :T} {:MY-FUNC {$ :T}}}
    }}}
    

            

The output looks like this:


            

::

    Hello, World!
    My Name is templ. I am the TEMplate Processing Language.
    Sometimes, templ likes to speak in the third person.
    
    templ can do math:
        1 + 1 = 2
        1 + 2 = 3
        2 + 3 = 5
        3 + 5 = 8
        etc...
    
    templ can operate on strings and lists:
        bananas
        [a, b, c, d, e, f]
    
    templ can do conditional processing:
        Phew!
    
    templ can loop (and do trig):
        sin(0) = 0.0
        sin(10) = 0.173648177667
        sin(20) = 0.342020143326
        sin(30) = 0.5
    
    
    templ can even do list comprehensions and user defined functions:
    Processing theta=40...
    Processing theta=50...
    Processing theta=60...
    Processing theta=70...
    {40:1.40883205281,
        50:1.40883205281,
        60:1.36602540378,
        70:1.28171276411}
        
        


.. _Section-2.2:

2.2: Code Generation - A Sine Lookup Table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            

The following template shows an example of how to use \ ``templ``\ 
to generate C-code, in this case a sine lookup table.


            

::

    {v
        {set :SIZE 10}
    }const double sine_lut[{get :SIZE}] =
    \{
    {for i {range {get :SIZE}} {::
        {let :THETA}
        {$ :THETA {mult
            {$ i}
            {div 360 {$ :SIZE}}
        }}
        {spit {'
            "    "
            {round 
                {sin {rad {$ :THETA}}}
                4
            }
            ,
            {\t}
            "// i = "
            {get i}
            ", theta = "
            {$ :THETA}
            " deg"
            {eol}
        }}
    }}\};
    

            

The output looks like this:


            

::

    const double sine_lut[10] =
    {
        0.0,	// i = 0, theta = 0 deg
        0.5878,	// i = 1, theta = 36 deg
        0.9511,	// i = 2, theta = 72 deg
        0.9511,	// i = 3, theta = 108 deg
        0.5878,	// i = 4, theta = 144 deg
        -0.0,	// i = 5, theta = 180 deg
        -0.5878,	// i = 6, theta = 216 deg
        -0.9511,	// i = 7, theta = 252 deg
        -0.9511,	// i = 8, theta = 288 deg
        -0.5878,	// i = 9, theta = 324 deg
    };
        



.. _Section-2.3:

2.3: Embedded Data
~~~~~~~~~~~~~~~~~~ 
            

The next example shows how \ ``templ``\  allows you to easily embed data
directly in the template file that uses it, allowing you to keep just
one file under version control, for instance. 


            

::

    
    {v
        %Embedded data
        {$ :DATA {'
            %   Name            Year    Month (-1)      Date
            {'  "Alan T."     1912    05              23 }
            {'  "John V."     1903    11              28 }
            {'  "Claude S."   1916    03              30 }
            {'  "George B."   1815    10              2  }
            {'  "George B."   1815    10              2  }
            {'  "Ada L."      1815    11              15 }
            {'  "Charles B."  1791    11              26 }
            {'  "Donald K."   1938    0               10 }
            {'  "Dennis R."   1941    8               9  }
        }}
    }{for :ROW {$ :DATA} {:
        {$ :STAMP {stamp {slice 1 {$ :ROW}}}}
        {$ :NOW {stamp}}
        {$ :AGE {floor {div {- {$ :NOW} {$ :STAMP}} {* 60 60 24 365.25}}}}
        {echo {@ 0 {$ :ROW}} ", age " {$ :AGE} " years." {eol} }
    }}

            

It produces this:


            

::

    
    Alan T., age 100 years.
    John V., age 109 years.
    Claude S., age 96 years.
    George B., age 197 years.
    George B., age 197 years.
    Ada L., age 197 years.
    Charles B., age 221 years.
    Donald K., age 75 years.
    Dennis R., age 71 years.
    
        
    


.. _Section-2.4:

2.4: Programmatic Invocation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The real power of \ ``templ``\  comes from the programmatic interface,
which allows you to predefine symbols, and even executables (functions, macros
and operators) in python, which are then accessible from the template.
Because, although \ ``templ``\  \ *is*\  Turing complete, and you \ *could*\  do all
of your processing directly in the template (or a separate included template), doing
advanced data processing in python can help keep your template files simpler. 



.. _Section-3:

3: Complete Contents
--------------------
.. contents::
    :depth: 10
