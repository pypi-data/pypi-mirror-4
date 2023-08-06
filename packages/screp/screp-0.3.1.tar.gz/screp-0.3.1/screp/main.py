import sys
from optparse import OptionParser
import lxml.etree as etree
import lxml.html as html
from lxml.cssselect import CSSSelector
import urlparse

from .format_parsers import (
        parse_csv_formatter,
        parse_json_formatter,
        parse_general_formatter,
        parse_anchor,
        )
from .context import (
        AnchorContextFactory,
        )
from .utils import raise_again
from .source import (
        URLDataSource,
        OpenedFileDataSource,
        FileDataSource,
        )


def report_error(e):
    print >>sys.stderr, "ERROR: %s" % (e,)


def report_warning(e):
    print >>sys.stderr, "WARNING: %s" % (e,)


def print_record(string):
    sys.stdout.write(string)


def get_formatter(anchors_factory):
    try:
        if [options.csv, options.json, options.general_format].count(None) != 2:
            raise ValueError("Only one of (--csv, --json, --format) may be specified!")

        if options.csv is not None:
            return parse_csv_formatter(options.csv, anchors_factory, header=options.csv_header)
        elif options.json is not None:
            return parse_json_formatter(options.json, anchors_factory, indent=options.json_indent)
        elif options.general_format is not None:
            return parse_general_formatter(options.general_format, anchors_factory, options.escaped)

        raise ValueError('No format defined!')
    except Exception as e:
        raise_again('Parsing format specification: %s' % (e,))


def get_selector(selector):
    try:
        return CSSSelector(selector)
    except Exception as e:
        raise_again('Parsing selector: %s' % (e,))


def get_anchor(string, anchors_factory):
    try:
        return parse_anchor(string, anchors_factory)
    except Exception as e:
        raise_again('Parsing anchor: %s' % (e,))


def make_anchors_factory(strings):
    factory = AnchorContextFactory((('$', 'element'), ('@', 'element')))

    for s in strings:
        a = get_anchor(s, factory)
        factory.add_anchor(a)

    return factory


def parse_xml_data(data):
    try:
        parser = etree.HTMLParser(remove_blank_text=True)

        return etree.fromstring(data, parser)
    except Exception as e:
        raise_again('Parsing document: %s' % (e,))


def handle_value_exception(e):
    if options.stop_on_error:
        raise
    elif options.show_warnings:
        report_warning(e)


def compute_value(substitor, context):
    try:
        return substitor.execute(context)
    except Exception as e:
        handle_value_exception(e)

        return options.null_value


def compute_anchor(anchor, context):
    try:
        return anchor.execute(context)
    except Exception as e:
        handle_value_exception(e)


def get_context(root, element, anchors):
    context = XMLContext(element, root)
    for a in anchors:
        v = compute_anchor(a, context)
        if v is not None:
            context.add_anchor(a.name, v)

    return context


def screp_source(formatter, terms, anchors_factory, selector, source):
    try:
        data = source.read_data()
        dom = parse_xml_data(data)
    except Exception as e:
        if options.continue_on_file_errors:
            return
        else:
            raise

    for e in selector(dom):
        context = anchors_factory.make_context({'$': e, '@': dom})

        print_record(formatter.format_record(map(lambda t: compute_value(t, context), terms)))


def screp_all(formatter, terms, anchors_factory, selector, sources):
    print_record(formatter.start_format())

    for source in sources:
        screp_source(formatter, terms, anchors_factory, selector, source)

    print_record(formatter.end_format())


def make_url_data_source(source):
    return URLDataSource(source, user_agent=options.user_agent, proxy=options.use_proxy)


def make_data_source(source):
    url = urlparse.urlparse(source)

    if url.scheme != '':
        return make_url_data_source(source)
    else:
        return FileDataSource(source)


def make_data_sources(sources):
    if len(sources) == 0:
        return [OpenedFileDataSource('STDIN', sys.stdin)]
    else:
        return map(make_data_source, sources)


def parse_cli_options(argv):
    parser = OptionParser()

    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False, help='verbose')
    parser.add_option('-n', '--null-value', dest='null_value', action='store',
            default='NULL', help='value to print when a value cannot be computed')
    parser.add_option('-e', '--stop-on-error', dest='stop_on_error', action='store_true',
            default=False, help='stop on first error; inhibits --null-value and --warnings')
    parser.add_option('-w', '--warnings', dest='show_warnings', action='store_true',
            default=False, help='show warnings or execution errors')
    parser.add_option('-c', '--csv', dest='csv', action='store', default=None,
            help='print records as csv rows')
    parser.add_option('-F', '--continue-on-file-errors', dest='continue_on_file_errors',
            action='store_true', default=False, help='ignore errors in reading and parsing data sources')
    parser.add_option('-a', '--anchor', dest='anchors', action='append', default=[],
            help='define secondary anchor, relative to the primary anchors, using the format <name>=<term>')
    parser.add_option('--csv-header', dest='csv_header', action='store',
           default=None, help='print csv header')
    parser.add_option('-d', '--debug', dest='debug', action='store_true', default=False,
            help='print debugging information on errors; implies -e')
    parser.add_option('-A', '--user-agent', dest='user_agent', action='store', default=None,
            help='user agent to use when retrieving URLs')
    parser.add_option('-j', '--json', dest='json', action='store',
            default=None, help='print record as json object')
    parser.add_option('--indent-json', dest='json_indent', action='store_true', default=False,
            help='indent json objects')
    parser.add_option('--no-proxy', dest='use_proxy', action='store_false', default=True,
            help="don't use proxy, even if environment variables are set")
    parser.add_option('-f', '--format', dest='general_format', action='store',
            default=None, help='print record as custom format')
    parser.add_option('-S', '--not-escaped', dest='escaped', action='store_false', default=True,
            help="don't unescape the general format")
#   parser.add_option('-U', '--base-url', dest='base_url', action='store',
#           default=None, help='base url to use when computing absolute urls')

    (options, args) = parser.parse_args(argv)

    if len(args) == 0:
        parser.print_usage(sys.stderr)
        sys.exit(1)

    selector = args[0]

    sources = args[1:]

    return (options, selector, sources)


def main():
    global options

    try:
        (options, selector, sources_raw) = parse_cli_options(sys.argv[1:])

        sources = make_data_sources(sources_raw)

        anchors_factory = make_anchors_factory(options.anchors)

        (formatter, terms) = get_formatter(anchors_factory)

        selector = get_selector(selector)

        screp_all(formatter, terms, anchors_factory, selector, sources)

    except Exception as e:
        if options.debug:
            raise
        else:
            report_error(e)

        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
