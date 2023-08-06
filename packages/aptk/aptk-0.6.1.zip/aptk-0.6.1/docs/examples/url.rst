URI Generic Syntax
==================

.. highlight:: aptk

In :rfc:`3986` there is embedded a grammar for parsing URIs::

    :grammar URI

In chapter 1.1.2. there is started with some examples, which can be used
as testcases for the grammar::

    <URI> ~~ ftp://ftp.co.za/rfc/rfc1808.txt
    <URI> ~~ http://www.ietf.org/rfc/rfc2396.txt
    <URI> ~~ ldap://[2001:db8::7]/c=GB?objectclass?one
    <URI> ~~ mailto:John.Doe@example.com
    <URI> ~~ news:comp.infosystems.www.servers.unix
    <URI> ~~ tel:+1-816-555-1212
    <URI> ~~ telnet://192.0.2.16:80/
    <URI> ~~ urn:oasis:names:specification:docbook:dtd:xml:4.1.2

For finding out which parts should be captured, an expected parse-tree 
can be added to some of the test-urls::

    <URI> ~~ ftp://ftp.co.za/rfc/rfc1808.txt 
          -> URI(
                 scheme( 'ftp' ),
                 authority( host( reg-name( 'ftp.co.za' ) ) ),
                 path( '/rfc/rfc1808.txt' )
             )
         
    <URI> ~~ ldap://[2001:db8::7]/c=GB?objectclass?one
          -> URI(
                 scheme( 'ldap' ),
                 authority( host( IPv6-address( '2001:db8::7' ) ) ),
                 path( '/c=GB' ),
                 query( 'objectclass?one' )
             )

    <URI> ~~ tel:+1-816-555-1212
          -> URI(
                 scheme( 'tel' ),
                 path( '+1-816-555-1212' )
             )

    <URI> ~~ urn:oasis:names:specification:docbook:dtd:xml:4.1.2
          -> URI(
                 scheme( 'urn' ),
                 path( 'oasis:names:specification:docbook:dtd:xml:4.1.2' )
             )

We add a test to match all parts::

    <URI> ~~ http://userinfo@foo.bar.com/some/path?some=query#fragment
          -> URI(
                 scheme( 'http' ),
                 authority(
                     userinfo( 'userinfo' ),
                     host( reg-name( 'foo.bar.com' ) ) ),
                 path( '/some/path' ),
                 query( 'some=query' ),
                 fragment( 'fragment' )
             )

Instead of doing the grammar 1-1 here, we create an aPTK optimized form::

    <URI>  ::= <scheme> ":" <.hier-part> [ "?" <query> ]? [ "#" <fragment> ]?

There are two more possible entry-points into the grammar::

    <URI-reference> ::= <.URI> | <.relative-ref>
    <absolute-URI>  ::= <scheme> ":" <.hier-part> [ "?" <query> ]?

Setup basic character-classes::

    alpha         = A-Z a-z
    digit         = 0-9
    unreserved    = {:alpha:} {:digit:} \- . ~
    gen-delims    = : / ? # \[ \] @
    sub-delims    = ! $ & ' ( ) * + , ; =
    reserved      = {:gen-delims:} {:sub-delims:}
    hexdigit      = 0-9 A-F a-f

Other basic tokens::

    pct-encoded   = % [{:hexdigit:}]{2}
    pchar         = [{:unreserved:} {:sub-delims:} : @] | {:pct-encoded:}
    pchar-qs      = [{:unreserved:} {:sub-delims:} : @ ? /] | {:pct-encoded:}

Paths can be created as (capturing) tokens::

    segment       = {pchar}*
    segment-nz    = {pchar}+
    segment-nz-nc = [ [{:unreserved:} {:sub-delims:} @] | {:pct-encoded:} ]+
    path-abempty  = (?P<path> [ / {segment} ]* )
    path-absolute = (?P<path> / [ {segment-nz} [ / {segment} ]* ]? )
    path-noscheme = (?P<path> {segment-nz-nc}  [ / {segment} ]* )
    path-rootless = (?P<path> {segment-nz}     [ / {segment} ]* )
    path-empty    = (?P<path> (?!{pchar}) )

And IP-addresses can also be parsed by tokens::

    h16         = [{:hexdigit:}]{1,4}
    h16c        = {:h16:} :
    dec-octet   = \d | [1-9]\d | 1\d\d | 2[0-4]\d | 25[0-5]
    IPv4-address = [ {dec-octet} ]{3} {dec-octet}
    ls32        = {:h16:} : {:h16:} | {IPv4-address}

    IPv6-address =                         {h16c}{6}{ls32}
                 |                      :: {h16c}{5}{ls32}
                 |               {h16}? :: {h16c}{4}{ls32}
                 | [ {h16c}{,1}{h16} ]? :: {h16c}{3}{ls32}
                 | [ {h16c}{,2}{h16} ]? :: {h16c}{2}{ls32}
                 | [ {h16c}{,3}{h16} ]? :: {h16c}{1}{ls32}
                 | [ {h16c}{,4}{h16} ]? ::          {ls32}
                 | [ {h16c}{,5}{h16} ]? ::          {h16}
                 | [ {h16c}{,6}{h16} ]? :: 

    reg-name     = [ [{:unreserved:}{:sub-delims:}] | {pct-encoded} ]+

    reg-name    := {reg-name}
    

Now rules are created top bottom in order of appearence::

    scheme      := [{:alpha:}][{:alpha:}{:digit:}+\-.]*

    hier-part   := "//" <authority> {path-abempty}
                  | {path-absolute}
                  | {path-rootless}
                  | {path-empty}

    authority   := [ <userinfo> "@" ]? <host> [ ":" <port> ]?

    port        := \d+

    userinfo    := [{:unreserved:}{:sub-delims:}:]*

    host        := <.IP-literal> | <IPv4-address> | <reg-name>

    IP-literal  := "[" [ <IPv6-address> | <IPvFuture> ] "]"

    IPvFuture   := "v" [{:hexdigit:}]+ "." [{:unreserved:}{:sub-delims:}:]+

    IPv4-address := {IPv4-address}
    IPv6-address := {IPv6-address}

    query        := {pchar-qs}*
    fragment     := {pchar-qs}*

    relative-ref := <.relative-part> [ "?" <query> ]? [ "#" <fragment> ]?

    relative-part := "//" <authority> {path-abempty}
                    | {path-absolute}
                    | {path-noscheme}
                    | {path-empty}

