from datetime import datetime, date, time
from collections import defaultdict
import re


def parse_urls_without_files(log):
    parser = re.search(r"(?<=./)[-.\w]+[.]\w+(?=[?\s])", log)
    return parser

def parse_urls(log):
    parser = re.search('(?<=//)[\w]*:?[\w]*@?[\w]*:?[\d]*[/]?[^?\s]*', log)
    if parser:
        return parser.group(0)
    else:
        return None

def parse_ignore_urls(log, ignore_urls):
    if log in ignore_urls:
        return True
    else:
        return False

def parse_urls_without_www(log):
    return re.sub(r"(?<=://)www.", "", log)

def start_at_time(log, start):
    parser = re.search("(?<=\[)\d{2}/\w+/\w{4}\s\w+:\w+:\w+", log)
    if parser:
        date_from_log = datetime.strptime(parser.group(0), '%d/%b/%Y %H:%M:%S')
        if start > date_from_log:
            return True
        else:
            return False

def stop_at_time(log, stop):
    parser = re.search("(?<=\[)\d{2}/\w+/\w{4}\s\w+:\w+:\w+", log)
    if parser:
        date_from_log = datetime.strptime(parser.group(0), '%d/%b/%Y %H:%M:%S')
        if stop < date_from_log:
            return True
        else:
            return False

def parse_urls_slow_quire(log):
    parser = re.search('(?<=://).*\s([\d]+)(?=\n)', log)
    if parser:
        edit_parser = re.search('^[\w]*:?[\w]*@?[\w]*:?[\d]*[/]?[^?\s]*', parser.group(1))
        return edit_parser.group()
    else:
        return None

def parse_by_request_type(log, request_type):
    parser = re.search('(?<=")\w+(?=.*://)', log)
    if parser:
        if request_type != parser.group():
            return True
        else:
            return False

def parse(
        ignore_files=False,
        ignore_urls=[],
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):
    """
    Основная функция
    """
    urls = defaultdict(lambda: {'querie_time': 0, 'count': 0})
    with open('log.log') as f:
        for line in f:
            if ignore_files:
                if parse_urls_without_files(line):
                    continue
            if ignore_urls:
                if parse_ignore_urls(line, ignore_urls):
                    continue
            if ignore_www:
                line = parse_urls_without_www(line) if parse_urls_without_www(line) else line
            if start_at:
                if start_at_time(line, start_at):
                    continue
            if stop_at:
                if stop_at_time(line, stop_at):
                    continue
            if request_type:
                if parse_by_request_type(line, request_type):
                    continue

            if slow_queries:
                if parse_urls_slow_quire(line):
                    urls[parse_urls(line)]['querie_time'] += int(parse_urls_slow_quire(line))
                    urls[parse_urls(line)]['count'] += 1

            else:
                if parse_urls(line):
                    urls[parse_urls(line)]['count'] += 1
    result = list()
    if slow_queries:
        for val in urls.values():
            result.append(val['querie_time'] // val['count'])
        result = sorted(result, reverse=True)
    else:
        urls = sorted(urls.items(), key=lambda x: x[1]['count'], reverse=True)
        result = [val[1]['count'] for val in urls]

    return result[:5]
