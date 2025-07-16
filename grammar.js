/**
 * See https://docs.oracle.com/en/java/javase/23/docs/specs/javadoc/doc-comment-spec.html for
 * more information on how javadocs work... in theory.
 * In the wild, these comments are a bit messier.
 *
 * @file Parser for Javadoc documentation comments
 * @author Robert Muir <rmuir@apache.org>
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: 'javadoc',

  // reads to the end of tag (brace balancing)
  externals: $ => [
    $.inline_description,
  ],

  extras: _ => [
    token(choice(
      // Skip over stars at the beginnings of lines
      seq(/\n/, /[ \t]*/, repeat(seq('*', /[ \t]*/))),
      /\s/,
    )),
  ],

  supertypes: $ => [
    $.inline_tag,
    $.block_tag,
  ],

  rules: {
    document: $ => choice(
      seq(
        $._multiline_begin,
        optional($.description),
        repeat($.block_tag),
        optional($._multiline_end),
      ),
      seq(
        $._singleline_begin,
        optional(choice(alias($.description, $.markdown_description), $.block_tag)),
      ),
    ),

    description: $ => repeat1(
      choice(
        $._text,
        $._inline_tag_actual,
        $._inline_tag_false_positive,
      ),
    ),

    // we are just an alias node to make it easier to apply appropriate injection
    markdown_description: _ => '',

    block_tag: $ => choice(
      $.author_tag,
      $.deprecated_tag,
      $.hidden_tag,
      $.param_tag,
      $.provides_tag,
      $.return_tag,
      $.see_tag,
      $.serial_tag,
      $.serial_data_tag,
      $.serial_field_tag,
      $.since_tag,
      $.spec_tag,
      $.throws_tag,
      $.uses_tag,
      $.version_tag,
      $.custom_tag,
    ),

    inline_tag: $ => choice(
      $.code_tag,
      $.doc_root_tag,
      $.index_tag,
      $.inherit_doc_tag,
      $.link_tag,
      $.literal_tag,
      alias($._inline_return_tag, $.return_tag),
      $.snippet_tag,
      $.summary_tag,
      $.system_property_tag,
      $.value_tag,
      $.custom_inline_tag,
    ),

    _inline_tag_actual: $ => seq(
      '{',
      $.inline_tag,
      '}',
    ),

    // cope with stray {, }, and * cats
    _inline_tag_false_positive: _ => choice(
      token(prec.left(1, /\{[^@]/)),
      token(prec.left(1, /\}/)),
      token.immediate(prec.left(1, /[ \t]*\*[^/]/)),
    ),

    author_tag: $ => seq(
      field('name', alias('@author', $.tag_name)),
      optional(field('name_text', $.description)),
    ),

    code_tag: $ => seq(
      field('name', alias('@code', $.tag_name)),
      optional(field('text', alias($.inline_description, $.code))),
    ),

    deprecated_tag: $ => seq(
      field('name', alias('@deprecated', $.tag_name)),
      optional(field('deprecated_text', $.description)),
    ),

    doc_root_tag: $ => field('name', alias('@docRoot', $.tag_name)),

    hidden_tag: $ => field('name', alias('@hidden', $.tag_name)),

    index_tag: $ => seq(
      field('name', alias('@index', $.tag_name)),
      choice(
        field('indexword', $.indexword),
        field('phrase', $.string_literal),
      ),
      optional(field('description', alias($.inline_description, $.description))),
    ),

    inherit_doc_tag: $ => seq(
      field('name', alias('@inheritDoc', $.tag_name)),
      optional(field('supertype', $.type)),
    ),

    link_tag: $ => seq(
      field('name', alias(choice('@link', '@linkplain'), $.tag_name)),
      field('reference', $.reference),
      optional(
        seq(
          $._space,
          optional(field('label', alias($.inline_description, $.description))),
        ),
      ),
    ),

    literal_tag: $ => seq(
      field('name', alias('@literal', $.tag_name)),
      optional(field('text', alias($.inline_description, $.literal))),
    ),

    param_tag: $ => seq(
      field('name', alias('@param', $.tag_name)),
      choice(
        seq(
          '<',
          field('type_parameter_name', $.type_parameter),
          '>',
        ),
        field('parameter_name', $.identifier),
      ),
      optional(field('description', $.description)),
    ),

    provides_tag: $ => seq(
      field('name', alias('@provides', $.tag_name)),
      field('service_type', $.type),
      optional(field('description', $.description)),
    ),

    return_tag: $ => seq(
      field('name', alias('@return', $.tag_name)),
      optional(field('description', $.description)),
    ),

    _inline_return_tag: $ => seq(
      field('name', alias('@return', $.tag_name)),
      optional(field('description', alias($.inline_description, $.description))),
    ),

    see_tag: $ => seq(
      field('name', alias('@see', $.tag_name)),
      choice(
        field('string', $.string_literal),
        field('url_title', $.url_title),
        field('reference', $.reference),
        seq(field('reference', $.reference), field('label', $.description)),
      ),
    ),

    serial_tag: $ => seq(
      field('name', alias('@serial', $.tag_name)),
      optional(choice(
        field('include', 'include'),
        field('exclude', 'exclude'),
        field('field_description', $.description),
      )),
    ),

    serial_data_tag: $ => seq(
      field('name', alias('@serialData', $.tag_name)),
      optional(field('data_description', $.description)),
    ),

    serial_field_tag: $ => seq(
      field('name', alias('@serialField', $.tag_name)),
      field('field_name', $.identifier),
      field('field_type', $.type),
      optional(field('field_description', $.description)),
    ),

    since_tag: $ => seq(
      field('name', alias('@since', $.tag_name)),
      optional(field('since_text', $.description)),
    ),

    snippet_tag: $ => seq(
      field('name', alias('@snippet', $.tag_name)),
      optional(field('attributes', $.attributes)),
      optional(seq(
        ':',
        token.immediate('\n'),
        field('body', alias($.inline_description, $.description)),
      )),
    ),

    spec_tag: $ => seq(
      field('name', alias('@spec', $.tag_name)),
      field('url', $.url),
      optional(field('title', $.description)),
    ),

    summary_tag: $ => seq(
      field('name', alias('@summary', $.tag_name)),
      optional(field('text', alias($.inline_description, $.description))),
    ),

    system_property_tag: $ => seq(
      field('name', alias('@systemProperty', $.tag_name)),
      optional(field('property_name', $.system_property)),
    ),

    throws_tag: $ => seq(
      field('name', alias(choice('@throws', '@exception'), $.tag_name)),
      field('exception_type', $.type),
      optional(field('description', $.description)),
    ),

    uses_tag: $ => seq(
      field('name', alias('@uses', $.tag_name)),
      field('service_type', $.type),
      optional(field('description', $.description)),
    ),

    value_tag: $ => seq(
      field('name', alias('@value', $.tag_name)),
      optional(
        field('format',
          choice(
            $.bare_format_string,
            $.literal_format_string,
          ),
        ),
      ),
      optional(
        field('field_reference', $.reference),
      ),
    ),

    version_tag: $ => seq(
      field('name', alias('@version', $.tag_name)),
      optional(field('version_text', $.description)),
    ),

    // generic block tag (e.g. custom doclet)
    custom_tag: $ => seq(
      field('name', $.tag_name),
      optional(field('description', $.description)),
    ),

    // generic inline tag (e.g. custom doclet)
    custom_inline_tag: $ => seq(
      field('name', $.tag_name),
      optional(field('description', alias($.inline_description, $.description))),
    ),

    attributes: $ => repeat1(
      $.attribute,
    ),

    attribute: $ => seq(
      field('name', $.identifier),
      optional(seq('=', field('value', $.attribute_value))),
    ),

    attribute_value: $ => choice(
      $.string_literal,
      $.identifier,
      $.unsigned_integer,
    ),

    // highly ambiguous due the ability to omit from both left and right sides
    reference: $ => choice(
      seq($.module, token.immediate('/'), $.type, $._fragment_or_member),
      seq($.module, token.immediate('/'), $.type),
      seq($.module, token.immediate('/')),
      seq($.type, $._fragment_or_member),
      $._fragment_or_member,
      alias($._qualified_identifier, $.type),
      $.member,
    ),

    _fragment_or_member: $ => choice(
      seq('##', $.fragment),
      seq('#', $.member),
    ),

    member: $ => choice(
      $.identifier,
      $.method,
    ),

    method: $ => seq(
      $.identifier,
      '(',
      optional($.parameters),
      ')',
    ),

    parameters: $ => seq(
      $.parameter,
      repeat(seq(',', $.parameter)),
    ),

    parameter: $ => seq(
      $.parameter_type,
      optional($._parameter_mods),
      optional(seq(field('name', $.identifier), optional($._parameter_mods))),
    ),

    parameter_type: $ => choice(
      $.boolean_type,
      $.integral_type,
      $.floating_point_type,
      $.type,
    ),

    _parameter_mods: _ => choice(
      repeat1(seq('[', ']')),
      '...',
    ),

    _space: _ => /[\s]+/,

    _qualified_identifier: $ => seq(
      $._type,
      '.',
      $.identifier,
    ),

    _type: $ => choice(
      $.identifier,
      $._qualified_identifier,
    ),

    module: $ => $._type,
    type: $ => $._type,

    boolean_type: _ => 'boolean',
    integral_type: _ => choice(
      'byte',
      'short',
      'int',
      'long',
      'char',
    ),
    floating_point_type: _ => choice(
      'float',
      'double',
    ),

    fragment: _ => /[a-zA-Z0-9_!$&'()+%=\-.~:?]+/,

    type_parameter: $ => $.identifier,

    tag_name: _ => /@[a-zA-Z0-9_.]+/,

    bare_format_string: _ => /%[^\s%]+/,
    literal_format_string: _ => seq('"', /[^"%]*[%][^"%]*/, '"'),

    system_property: $ => seq(repeat(seq($.identifier, '.')), $.identifier),
    string_literal: $ => seq('"', $.quoted_value, '"'),
    quoted_value: _ => /[^"]+/,
    url_title: $ => seq('<', $.description),
    url: _ => /[^\s]+/,
    indexword: _ => /[a-zA-Z]+/,

    unsigned_integer: _ => /[0-9]+/,
    identifier: _ => /[\p{XID_Start}_$][\p{XID_Continue}\u00A2_$]*/u,

    literal: _ => /[^}]+/,
    code: $ => $._text,

    _text: _ => token(prec(-1, /[^*{}@\s][^*{}\n]*([^*/{}\n][^*{}\n]*\*+)*/)),

    _multiline_begin: _ => '/**',

    _multiline_end: _ => '*/',

    _singleline_begin: _ => '///',
  },
});
