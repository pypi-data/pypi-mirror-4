var _ref,
  __hasProp = Object.prototype.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

window.cldoc = $.extend($.extend({
  host: document.location.href.substring(0, document.location.href.lastIndexOf('/'))
}, (_ref = window.cldoc) != null ? _ref : {}), {
  tag: function(node) {
    return $.map(node, function(e) {
      return e.tagName.toLowerCase();
    });
  },
  startswith: function(s, prefix) {
    return s.indexOf(prefix) === 0;
  }
});

$(document).ready(function() {
  cldoc.Sidebar.init();
  return cldoc.Page.route();
});

cldoc.SearchWorker = function() {
  var bsearch, db, load_db, log, search_term,
    _this = this;
  db = null;
  log = function(msg) {
    return self.postMessage({
      type: 'log',
      message: msg
    });
  };
  load_db = function(host) {
    var xhr;
    xhr = new XMLHttpRequest();
    xhr.open('GET', host + '/search.json?' + new Date().getTime(), false);
    xhr.send();
    return JSON.parse(xhr.responseText);
  };
  bsearch = function(term, l, r, sel) {
    var mid, rec, suf, suffix_record, _ref2;
    suffix_record = function(i) {
      return db.suffixes[i][0];
    };
    while (l < r) {
      mid = Math.floor((l + r) / 2);
      rec = suffix_record(mid);
      suf = db.records[rec[0]][0].substring(rec[1]);
      _ref2 = sel(suf) ? [mid + 1, r] : [l, mid], l = _ref2[0], r = _ref2[1];
    }
    return [l, r];
  };
  search_term = function(term) {
    var end, l, r, start, t, _, _ref2, _ref3;
    if (term.length < 3) return [0, 0];
    l = 0;
    r = db.suffixes.length;
    t = term.toLowerCase();
    _ref2 = bsearch(t, 0, db.suffixes.length, function(suf) {
      return t > suf;
    }), start = _ref2[0], _ = _ref2[1];
    _ref3 = bsearch(t, start, db.suffixes.length, function(suf) {
      return suf.indexOf(t) === 0;
    }), _ = _ref3[0], end = _ref3[1];
    return [start, end];
  };
  return self.onmessage = function(ev) {
    var end, i, items, m, rec, recid, records, ret, rr, start, word, words, _i, _j, _len, _len2, _ref2, _ref3;
    m = ev.data;
    if (db === null) db = load_db(m.host);
    words = m.q.split(/\s+/);
    records = {};
    ret = {
      type: 'result',
      id: m.id,
      q: m.q,
      words: words,
      records: []
    };
    for (_i = 0, _len = words.length; _i < _len; _i++) {
      word = words[_i];
      _ref2 = search_term(word), start = _ref2[0], end = _ref2[1];
      for (i = start, _ref3 = end - 1; i <= _ref3; i += 1) {
        items = db.suffixes[i];
        for (_j = 0, _len2 = items.length; _j < _len2; _j++) {
          rec = items[_j];
          recid = rec[0];
          if (!(recid in records)) {
            rr = {
              name: db.records[recid][0],
              id: db.records[recid][1],
              score: 0,
              results: [],
              suffixhash: {}
            };
            ret.records.push(rr);
            records[recid] = rr;
          } else {
            rr = records[recid];
          }
          if (!(rec[1] in rr.suffixhash)) {
            rr.score += 1;
            rr.results.push([rec[1], rec[1] + word.length]);
            rr.suffixhash[rec[1]] = true;
          }
        }
      }
    }
    ret.records.sort(function(a, b) {
      var _ref4, _ref5;
      return (_ref4 = a.score > b.score) != null ? _ref4 : (_ref5 = a.score < b.score) != null ? _ref5 : -{
        1: 0
      };
    });
    return self.postMessage(ret);
  };
};

cldoc.SearchDb = (function() {

  function SearchDb() {
    var blob, wurl, _ref2,
      _this = this;
    this.searchid = 0;
    this.searchcb = null;
    wurl = (_ref2 = window.webkitURL) != null ? _ref2 : window;
    blob = new Blob(['worker = ' + cldoc.SearchWorker.toString() + '; worker();'], {
      type: 'text/javascript'
    });
    this.worker = new Worker(wurl.createObjectURL(blob));
    this.worker.onmessage = function(msg) {
      var m;
      m = msg.data;
      if (m.type === 'log') {
        return console.log(m.message);
      } else if (m.type === 'result') {
        if (m.id !== _this.searchid) return;
        _this.searchid = 0;
        return _this.searchcb(m);
      }
    };
  }

  SearchDb.prototype.search = function(q, cb) {
    this.searchid += 1;
    this.searchcb = cb;
    return this.worker.postMessage({
      type: 'search',
      q: q,
      id: this.searchid,
      host: cldoc.host
    });
  };

  return SearchDb;

})();

cldoc.Page = (function() {

  function Page() {}

  Page.pages = {};

  Page.current_page = null;

  Page.first = true;

  Page.search = {
    db: null
  };

  Page.request_page = function(page, cb) {
    var url,
      _this = this;
    if (page in this.pages) {
      cb(this.pages[page]);
      return;
    }
    if (page === '(report)') {
      url = 'report.xml';
    } else {
      url = 'xml/' + page + '.xml';
    }
    return $.ajax({
      url: url,
      cache: false,
      success: function(data) {
        _this.pages[page] = {
          xml: $(data),
          html: null
        };
        return cb(_this.pages[page]);
      }
    });
  };

  Page.load = function(page, scrollto, updatenav) {
    var _this = this;
    cldoc.Sidebar.exit_search();
    if (page === null || page === 'undefined') page = this.current_page;
    if (!page) page = 'index';
    if (updatenav) this.push_nav(page, scrollto);
    if (this.current_page !== page) {
      return this.request_page(page, function() {
        return _this.load_page(page, scrollto);
      });
    } else {
      return this.scroll(page, scrollto);
    }
  };

  Page.know_more = function(ref) {
    var a;
    a = this.make_link(ref, 'more information on separate page...');
    a.addClass('know_more');
    return a;
  };

  Page.make_link = function(ref, name) {
    var a,
      _this = this;
    a = $('<a/>', {
      href: this.make_internal_ref(ref)
    }).text(name);
    a.on('click', function() {
      _this.load_ref(ref);
      return false;
    });
    return a;
  };

  Page.load_page = function(page, scrollto) {
    var brief, cpage, data, html, root, title;
    this.first = this.current_page === null;
    this.current_page = page;
    cpage = this.pages[page];
    data = cpage.xml;
    html = cpage.html;
    $('#cldoc #cldoc_content').children().detach();
    root = data.children(':first');
    if (html) {
      $('#cldoc #cldoc_content').append(html.content);
      cldoc.Sidebar.load_html(html.sidebar);
    } else {
      cpage.html = {
        sidebar: cldoc.Sidebar.load(root),
        content: this.load_contents(root)
      };
    }
    title = root.attr('name');
    if (!title) {
      brief = root.children('brief');
      if (brief.length > 0) {
        title = brief.text();
        if (title[title.length - 1] === '.') {
          title = title.substring(0, title.length - 1);
        }
      }
    }
    if (!title) title = 'Documentation';
    document.title = title;
    return this.scroll(page, scrollto, true);
  };

  Page.make_external_ref = function(page, id) {
    if (page[0] === '#') page = page.substring(1);
    if (!id) {
      return page.replace('/', '#');
    } else {
      return page + '#' + id;
    }
  };

  Page.make_internal_ref = function(page, id) {
    if (!page) return '/';
    if (!id) {
      return '#' + page.replace('#', '/');
    } else {
      return '#' + page + '/' + id;
    }
  };

  Page.split_ref = function(ref) {
    return ref.split('#', 2);
  };

  Page.load_ref = function(ref) {
    var r;
    r = this.split_ref(ref);
    return this.load(r[0], r[1], true);
  };

  Page.make_header = function(item) {
    var id, ret, title, type;
    id = item.attr('id');
    if (id) {
      ret = $('<span/>');
      type = this.node_type(item);
      if (type) $('<span class="keyword"/>').text(type.title[0]).appendTo(ret);
      title = item.attr('title');
      if (title) {
        $('<span/>').text(title).appendTo(ret);
      } else {
        $('<span/>').text(id).appendTo(ret);
      }
      return ret;
    } else {
      return null;
    }
  };

  Page.load_description = function(page, content) {
    var desc, doc, h1, id;
    doc = new cldoc.Doc(page.children('doc')).render();
    id = page.attr('id');
    if (id) {
      h1 = $('<h1/>').appendTo(content);
      h1.attr('id', id);
      h1.append(this.make_header(page));
    }
    if (doc) {
      desc = $('<div class="description"/>');
      desc.append(doc);
      return content.append(desc);
    }
  };

  Page.node_type = function(item) {
    var typename;
    typename = cldoc.tag(item)[0];
    if (!(typename in cldoc.Node.types)) return null;
    return cldoc.Node.types[typename];
  };

  Page.load_items = function(page, content) {
    var all, container, group, h2, item, items, tp, type, _i, _j, _len, _len2, _ref2, _results;
    all = page.children();
    _ref2 = cldoc.Node.groups;
    _results = [];
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      group = _ref2[_i];
      items = all.filter(group);
      if (items.length === 0) continue;
      type = this.node_type(items);
      if (!type || type === cldoc.Node.types.report) continue;
      h2 = $('<h2/>').text(type.title[1]);
      h2.attr('id', type.title[1].toLowerCase());
      h2.appendTo(content);
      container = type.render_container();
      for (_j = 0, _len2 = items.length; _j < _len2; _j++) {
        item = items[_j];
        item = $(item);
        if (cldoc.tag(item)[0] !== cldoc.tag(items)[0]) {
          tp = this.node_type(item);
        } else {
          tp = type;
        }
        if (tp) new tp($(item)).render(container);
      }
      if (container) {
        _results.push(content.append(container));
      } else {
        _results.push(void 0);
      }
    }
    return _results;
  };

  Page.load_contents = function(page) {
    var content;
    content = $('#cldoc #cldoc_content');
    content.children().detach();
    this.load_description(page, content);
    this.load_items(page, content);
    return content.children();
  };

  Page.push_nav = function(page, scrollto) {
    return history.pushState({
      page: page,
      scrollto: scrollto
    }, page, this.make_internal_ref(page, scrollto));
  };

  Page.route = function() {
    var hash, m, page, route, scrollto,
      _this = this;
    hash = document.location.hash.substr(1);
    route = new RegExp('^([^/]+)(/(.*))?$');
    m = route.exec(hash);
    page = '';
    scrollto = '';
    if (!m) {
      page = 'index';
    } else {
      page = m[1];
      scrollto = m[3];
    }
    $(window).on('popstate', function(e) {
      var state;
      if (e.originalEvent.state) {
        state = e.originalEvent.state;
        if (state.page !== _this.current_page) {
          return _this.load(state.page, state.scrollto, false);
        } else {
          return _this.select(state.scrollto);
        }
      }
    });
    return this.load(page, scrollto);
  };

  Page.select = function(scrollto, doanimate) {
    var inopts, outopts;
    scrollto = $(scrollto);
    if (!scrollto && !this.selected_element) return;
    if (scrollto && this.selected_element && scrollto.attr('id') === this.selected_element.attr('id')) {
      return;
    }
    if (doanimate) {
      inopts = {
        'duration': 2000,
        'easing': 'easeInOutExpo'
      };
      outopts = {
        'duration': 100,
        'easing': 'easeInOutExpo'
      };
    } else {
      inopts = {
        'duration': 0
      };
      outopts = {
        'duration': 0
      };
    }
    if (this.selected_element) {
      this.selected_element.removeClass('selected', outopts);
      this.selected_element = null;
    }
    if (scrollto) {
      this.selected_element = $(scrollto);
      return this.selected_element.addClass('selected', inopts);
    }
  };

  Page.scroll = function(page, scrollto, newpage) {
    var e, istopandnew, top;
    if (!scrollto) return;
    if (page === null) page = this.current_page;
    e = document.getElementById(scrollto);
    if (e) {
      e = $(e);
      top = e.offset().top - 10;
      istopandnew = newpage && e.is('h1');
      if (this.first || istopandnew) {
        if (!istopandnew) {
          this.select(e);
        } else {
          this.select();
        }
        $('html, body').scrollTop(top);
      } else {
        this.select(e, true);
        $('html, body').animate({
          scrollTop: top
        }, 1000, 'easeInOutExpo');
      }
    } else {
      this.select(null, true);
    }
    return this.first = false;
  };

  Page.render_search = function(result) {
    var a, content, cpage, data, end, item, page, pageid, parts, prev, records, res, sortfunc, start, t, tag, _i, _j, _k, _len, _len2, _len3, _ref2, _ref3, _ref4, _ref5,
      _this = this;
    content = $('#cldoc_content');
    content.children().detach();
    $('<h1><span class="keyword">Search</span> </h1>').append(result.q).appendTo(content);
    if (result.records.length === 0) {
      $('<span class="info">There were no results for this search query.</span>').appendTo(content);
      cldoc.Sidebar.render_search([]);
      $('html, body').scrollTop(0);
      return;
    }
    records = [];
    _ref2 = result.records;
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      res = _ref2[_i];
      _ref3 = this.split_ref(res.id), page = _ref3[0], pageid = _ref3[1];
      if (!page in this.pages) continue;
      cpage = this.pages[page];
      data = cpage.xml;
      item = $(data[0].getElementById(pageid));
      if (item.length !== 1) continue;
      tag = cldoc.tag(item)[0];
      res.type = tag;
      res.brief = new cldoc.Doc(item.children('brief'));
      res.page = page;
      res.qid = pageid;
      records.push(res);
    }
    sortfunc = function(a, b) {
      var ai, bi;
      if (a.score !== b.score) {
        if (a.score > b.score) {
          return -1;
        } else {
          return 1;
        }
      }
      if (a.type !== b.type) {
        ai = cldoc.Node.order[a.type];
        bi = cldoc.Node.order[b.type];
        if (ai !== bi) {
          if (ai < bi) {
            return -1;
          } else {
            return 1;
          }
        }
      }
      if (a.name < b.name) {
        return -1;
      } else {
        return 1;
      }
    };
    records.sort(sortfunc);
    t = $('<table class="search_results"/>').appendTo(content);
    for (_j = 0, _len2 = records.length; _j < _len2; _j++) {
      res = records[_j];
      res.results.sort(function(a, b) {
        if (a[0] !== b[0]) {
          if (a[0] < b[0]) {
            return -1;
          } else {
            return 1;
          }
        }
        if (a[1] > b[1]) return -1;
        if (a[1] < b[1]) return 1;
        return 0;
      });
      prev = 0;
      parts = [];
      _ref4 = res.results;
      for (_k = 0, _len3 = _ref4.length; _k < _len3; _k++) {
        _ref5 = _ref4[_k], start = _ref5[0], end = _ref5[1];
        if (start < prev) continue;
        parts.push(res.qid.substring(prev, start));
        parts.push($('<span class="search_result"/>').text(res.qid.substring(start, end)));
        prev = end;
      }
      parts.push(res.qid.substring(prev, res.qid.length));
      a = $('<a/>', {
        href: this.make_internal_ref(res.id)
      }).html(parts);
      a.on('click', function() {
        _this.load_ref(res.id);
        return false;
      });
      $('<tr/>').append($('<td class="keyword"/>').text(res.type)).append($('<td class="identifier"/>').html(a)).appendTo(t);
      $('<tr/>').append($('<td/>')).append($('<td/>').html(res.brief.render())).appendTo(t);
    }
    cldoc.Sidebar.render_search(records);
    return $('html, body').scrollTop(0);
  };

  Page.search_result = function(result) {
    var page, pageid, pagereqcount, pages, record, _i, _len, _ref2, _ref3, _results,
      _this = this;
    pagereqcount = 0;
    pages = {};
    _ref2 = result.records;
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      record = _ref2[_i];
      _ref3 = this.split_ref(record.id), page = _ref3[0], pageid = _ref3[1];
      if (page in pages) continue;
      pagereqcount += 1;
      pages[page] = true;
    }
    if (pagereqcount === 0) this.render_search(result);
    _results = [];
    for (page in pages) {
      _results.push(this.request_page(page, function() {
        pagereqcount -= 1;
        if (pagereqcount === 0) return _this.render_search(result);
      }));
    }
    return _results;
  };

  Page.search = function(q) {
    var _this = this;
    if (q.length < 3) return false;
    if (!this.search.db) this.search.db = new cldoc.SearchDb();
    this.search.db.search(q, function(res) {
      return _this.search_result(res);
    });
    return true;
  };

  Page.exit_search = function() {
    var ref;
    ref = Page.make_external_ref(document.location.hash.substring(1));
    cldoc.Sidebar.exit_search();
    this.current_page = null;
    return this.load_ref(ref);
  };

  return Page;

})();

cldoc.Sidebar = (function() {

  function Sidebar() {}

  Sidebar.init = function() {
    var close, div, exitsearch, icon, input, it, items, sidebar,
      _this = this;
    sidebar = $('#cldoc #cldoc_sidebar');
    if (!sidebar) return;
    items = $('<div/>').attr('id', 'cldoc_sidebar_items');
    it = items[0];
    items.on('DOMSubtreeModified', function(e) {
      if (it.scrollHeight > it.clientHeight) {
        return $(it).removeClass('hide_scrollbar');
      } else {
        return $(it).addClass('hide_scrollbar');
      }
    });
    sidebar.append(items);
    div = $('<div/>').attr('id', 'cldoc_search');
    icon = $('<div class="icon"/>');
    close = $('<div class="close" title="Cancel search"/>');
    input = $('<input type="text" accesskey="s" title="Search documentation (Alt+S)"/>');
    items = $().add(div).add(icon).add(close);
    input.on('focus', function(e) {
      return items.addClass('focus');
    });
    $('body').on('keydown', function(e) {
      if (e.altKey && e.keyCode === 83) {
        input.focus();
        input.select();
        return true;
      }
    });
    input.on('blur', function() {
      return items.removeClass('focus');
    });
    icon.on('click', function() {
      return input.focus();
    });
    exitsearch = function() {
      input.val('');
      input.blur();
      return cldoc.Page.exit_search();
    };
    close.on('click', exitsearch);
    input.on('keypress', function(e) {
      if (e.charCode === 13) {
        cldoc.Page.search(input.val());
        return true;
      }
    });
    input.on('keydown', function(e) {
      if (e.keyCode === 27) return exitsearch();
    });
    div.append(icon);
    div.append(input);
    div.append(close);
    return sidebar.append(div);
  };

  Sidebar.render_search = function(results) {
    return $('#cldoc_sidebar').addClass('search');
  };

  Sidebar.exit_search = function() {
    return $('#cldoc_sidebar').removeClass('search');
  };

  Sidebar.load_html = function(html) {
    var items;
    items = $('#cldoc #cldoc_sidebar #cldoc_sidebar_items');
    items.children().detach();
    return items.append(html);
  };

  Sidebar.load = function(page) {
    var a, div, group, head, id, items, l, name, onpage, parts, _i, _len, _ref2;
    items = $('#cldoc #cldoc_sidebar #cldoc_sidebar_items');
    if (items.length === 0) return null;
    items.children().detach();
    head = cldoc.Page.make_header(page);
    if (head) {
      div = $('<div class="back"/>');
      name = $('<div class="name"/>');
      name.append(head);
      div.append(name);
      items.append(div);
      id = page.attr('id');
      parts = id.split('::');
      l = parts.slice(0, parts.length - 1).join('::');
      a = cldoc.Page.make_link(l);
      a.addClass('back');
      a.html('<span class="arrow">&crarr;</span>');
      if (parts.length === 1) {
        a.append($('<span>Index</span>'));
      } else {
        a.append($('<span/>').text(parts[parts.length - 2]));
      }
      div.append(a);
    }
    onpage = page.children().filter(':not([access]), [access=protected], [access=public]');
    _ref2 = cldoc.Node.groups;
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      group = _ref2[_i];
      this.load_group(items, page, onpage.filter(group));
    }
    return $('#cldoc_sidebar_items').children();
  };

  Sidebar.load_group = function(container, page, items) {
    var a, brief, cnt, cnti, ftag, isprot, isvirt, item, li, nm, prev, tp, type, ul, _i, _len,
      _this = this;
    if (items.length === 0) return;
    ftag = cldoc.tag($(items[0]))[0];
    type = cldoc.Page.node_type(items);
    if (!type) return;
    $('<div class="subtitle"/>').text(type.title[1]).appendTo(container);
    ul = $('<ul/>');
    prev = null;
    for (_i = 0, _len = items.length; _i < _len; _i++) {
      item = items[_i];
      item = $(item);
      if (cldoc.tag(item)[0] !== ftag) {
        tp = cldoc.Page.node_type(item);
      } else {
        tp = type;
      }
      if (!tp) continue;
      item = new tp(item);
      if ('render_sidebar' in item) {
        item.render_sidebar(ul);
        continue;
      }
      if (prev && prev.name === item.name) {
        cnt = prev.li.find('.counter');
        cnti = cnt.text();
        if (!cnti) {
          cnt.text('2');
        } else {
          cnt.text(parseInt(cnti) + 1);
        }
        cnt.css('display', 'inline-block');
        continue;
      }
      nm = item.sidebar_name();
      a = $('<a/>', {
        href: cldoc.Page.make_internal_ref(cldoc.Page.current_page, item.id)
      }).append(nm);
      li = $('<li/>');
      a.on('click', (function(item) {
        return function() {
          cldoc.Page.load(cldoc.Page.current_page, item.id, true);
          return false;
        };
      })(item));
      prev = {
        'name': item.name,
        'item': item,
        'li': li
      };
      a.append($('<span class="counter"/>'));
      isvirt = item.node.attr('virtual');
      isprot = item.node.attr('access') === 'protected';
      if (isprot && isvirt) {
        li.append($('<span class="protected virtual">p&nbsp;v</span>'));
      } else if (isprot) {
        li.append($('<span class="protected">p</span>'));
      } else if (isvirt) {
        li.append($('<span class="virtual">v</span>'));
      }
      li.append(a);
      brief = new cldoc.Doc(item.brief).render();
      if (brief) brief.appendTo(li);
      ul.append(li);
    }
    return ul.appendTo(container);
  };

  return Sidebar;

})();

cldoc.Node = (function() {

  Node.types = {};

  Node.groups = ['coverage', 'arguments', 'references', 'category', 'namespace', 'base', 'subclass', 'typedef', 'class, classtemplate', 'struct', 'enum', 'field, union', 'variable', 'constructor', 'destructor', 'method', 'function', 'report'];

  Node.order = {
    'category': 0,
    'namespace': 1,
    'base': 2,
    'subclass': 3,
    'typedef': 4,
    'class': 5,
    'classtemplate': 5,
    'struct': 6,
    'enum': 7,
    'enumvalue': 8,
    'field': 9,
    'union': 10,
    'variable': 11,
    'constructor': 12,
    'destructor': 13,
    'method': 14,
    'function': 15
  };

  function Node(node) {
    this.node = node;
    if (!this.node) return;
    if (this.node.length === 0) {
      this.node = null;
      return;
    }
    this.name = this.node.attr('name');
    this.id = this.node.attr('id');
    this.ref = this.node.attr('ref');
    if (this.ref && !this.id) this.id = this.ref.replace('#', '+');
    this.brief = node.children('brief').first();
    this.doc = node.children('doc').first();
  }

  Node.prototype.sidebar_name = function() {
    return this.name;
  };

  Node.render_container = function() {
    return $('<div/>', {
      'class': this.title[1].toLowerCase()
    });
  };

  Node.prototype.render = function(container) {
    return null;
  };

  return Node;

})();

cldoc.Type = (function(_super) {

  __extends(Type, _super);

  function Type(node) {
    var a, subtype;
    this.node = node;
    Type.__super__.constructor.call(this, this.node);
    this.qualifier = this.node.attr('qualifier');
    this.size = this.node.attr('size');
    this.typeparts = [];
    subtype = this.node.children('type');
    if (subtype.length > 0) {
      this.subtype = new Type(subtype);
      this.typeparts = this.typeparts.concat(this.subtype.typeparts);
    }
    if (this.name) {
      if (this.ref) {
        a = cldoc.Page.make_link(this.ref, this.name);
        this.typeparts.push(a);
      } else {
        this.typeparts.push($('<span class="name"/>').text(this.name));
      }
    }
    if (this.qualifier) {
      this.typeparts.push($('<span class="qualifier"/>').text(' ' + this.qualifier + ' '));
    }
    if (this.size) {
      this.typeparts.push($('<span class="array_size"/>').text('[' + this.size + ']'));
    }
  }

  Type.prototype.render = function() {
    var item, ret, _i, _len, _ref2;
    ret = $('<span class="type"/>');
    if (this.node.attr('builtin')) ret.addClass('builtin');
    _ref2 = this.typeparts;
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      item = _ref2[_i];
      ret.append(item);
    }
    return ret;
  };

  return Type;

})(cldoc.Node);

cldoc.Node.types.type = cldoc.Type;

cldoc.Doc = (function(_super) {

  __extends(Doc, _super);

  Doc.magic_separator = '%~@#~!';

  function Doc(node) {
    this.node = node;
    Doc.__super__.constructor.call(this, this.node);
  }

  Doc.either = function(node) {
    var brief, doc;
    doc = this.doc(node);
    if (doc) return doc;
    brief = this.brief(node);
    if (brief) return brief;
    return $();
  };

  Doc.brief = function(node) {
    return new Doc(node.children('brief')).render();
  };

  Doc.doc = function(node) {
    return new Doc(node.children('doc')).render();
  };

  Doc.prototype.escape = function(text) {
    var r;
    r = /([*_\\`{}#+-.!\[\]])/g;
    return text.replace(r, function(m) {
      return "\\" + m;
    });
  };

  Doc.prototype.process_markdown = function(text) {
    var a, converter, html, i, parts, rethtml, _ref2;
    converter = new Showdown.converter();
    html = converter.makeHtml(text);
    parts = html.split(Doc.magic_separator);
    rethtml = '';
    for (i = 0, _ref2 = parts.length - 2; i <= _ref2; i += 3) {
      a = cldoc.Page.make_link(parts[i + 1], parts[i + 2]);
      rethtml += parts[i] + a[0].outerHTML;
    }
    return rethtml + parts[parts.length - 1];
  };

  Doc.prototype.process_code = function(code) {
    var c, container, ret, span, tag, text, _i, _len, _ref2;
    ret = $('<pre/>');
    container = $('<code/>').appendTo(ret);
    _ref2 = $(code).contents();
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      c = _ref2[_i];
      if (c.nodeType === document.ELEMENT_NODE) {
        tag = c.tagName.toLowerCase();
        c = $(c);
        if (tag === 'ref') {
          cldoc.Page.make_link(c.attr('ref'), c.attr('name')).appendTo(container);
        } else {
          span = $('<span/>').text(c.text()).appendTo(container);
          span.addClass(tag);
        }
      } else {
        text = $(c).text();
        container.append(text);
      }
    }
    return ret;
  };

  Doc.prototype.render = function() {
    var a, astext, c, container, contents, href, msep, tag, _i, _j, _len, _len2, _ref2;
    if (!this.node) return null;
    container = $('<div/>', {
      'class': cldoc.tag(this.node)[0]
    });
    contents = this.node.contents();
    astext = '';
    msep = Doc.magic_separator;
    for (_i = 0, _len = contents.length; _i < _len; _i++) {
      c = contents[_i];
      if (c.nodeType === document.ELEMENT_NODE) {
        tag = c.tagName.toLowerCase();
        if (tag === 'ref') {
          c = $(c);
          astext += this.escape(msep + c.attr('ref') + msep + c.text() + msep);
        } else if (tag === 'code') {
          if (astext) {
            container.append(this.process_markdown(astext));
            astext = '';
          }
          container.append(this.process_code(c));
        }
      } else {
        astext += $(c).text();
      }
    }
    if (astext) container.append(this.process_markdown(astext));
    _ref2 = container.find('a');
    for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
      a = _ref2[_j];
      a = $(a);
      href = a.attr('href');
      if (href[0] === '#') {
        a.on('click', (function(href) {
          return function() {
            cldoc.Page.load_ref(cldoc.Page.make_external_ref(href));
            return false;
          };
        })(href));
      }
    }
    return container;
  };

  return Doc;

})(cldoc.Node);

cldoc.Node.types.doc = cldoc.Doc;

cldoc.Category = (function(_super) {

  __extends(Category, _super);

  Category.title = ['Category', 'Categories'];

  function Category(node) {
    this.node = node;
    Category.__super__.constructor.call(this, this.node);
  }

  Category.prototype.render = function(container) {
    var a, cat, categories, div, row, tb, _i, _len;
    div = $('<div class="item"/>');
    container.append(div);
    a = cldoc.Page.make_link(this.ref, this.name);
    a.attr('id', this.id);
    div.append(a);
    div.append(new cldoc.Doc(this.brief).render());
    categories = this.node.children('category');
    if (categories.length > 0) {
      tb = $('<table class="category"/>');
      for (_i = 0, _len = categories.length; _i < _len; _i++) {
        cat = categories[_i];
        cat = $(cat);
        row = $('<tr/>');
        a = cldoc.Page.make_link(cat.attr('ref'), cat.attr('name'));
        row.append($('<td/>').append(a));
        row.append($('<td class="doc"/>').append(cldoc.Doc.either(cat)));
        tb.append(row);
      }
      return div.append(tb);
    }
  };

  return Category;

})(cldoc.Node);

cldoc.Node.types.category = cldoc.Category;

cldoc.Enum = (function(_super) {

  __extends(Enum, _super);

  Enum.title = ['Enum', 'Enumerations'];

  function Enum(node) {
    this.node = node;
    Enum.__super__.constructor.call(this, this.node);
  }

  Enum.prototype.render = function(container) {
    var brief, doc, doctd, id, isprot, n, name, nm, row, sp, table, value, _i, _len, _ref2, _results;
    id = $('<span class="identifier"/>');
    if (!cldoc.startswith(this.name, '(anonymous')) id.text(this.name);
    isprot = this.node.attr('access') === 'protected';
    if (isprot) {
      n = 'protected enum';
    } else {
      n = 'enum';
    }
    if (this.node.attr('class')) n += ' class';
    if (this.node.attr('typedef')) n = 'typedef ' + n;
    sp = $('<span class="keyword"/>').text(n);
    name = $('<div/>').append(sp).append(' ');
    name.attr('id', this.id);
    name.append(id);
    container.append(name);
    doc = new cldoc.Doc(this.doc).render();
    if (doc) {
      container.append(doc);
    } else {
      brief = new cldoc.Doc(this.doc).render();
      if (brief) container.append(brief);
    }
    table = $('<table/>');
    container.append(table);
    _ref2 = this.node.children('enumvalue');
    _results = [];
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      value = _ref2[_i];
      value = $(value);
      row = $('<tr/>');
      row.attr('id', value.attr('id'));
      nm = $('<td class="name identifier"/>').text(value.attr('name'));
      row.append(nm);
      row.append($('<td class="value"/>').text(value.attr('value')));
      doctd = $('<td class="doc"/>').appendTo(row);
      doctd.append(cldoc.Doc.either(value));
      _results.push(table.append(row));
    }
    return _results;
  };

  return Enum;

})(cldoc.Node);

cldoc.Node.types["enum"] = cldoc.Enum;

cldoc.Struct = (function(_super) {

  __extends(Struct, _super);

  Struct.title = ['Struct', 'Structures'];

  function Struct(node) {
    this.node = node;
    Struct.__super__.constructor.call(this, this.node);
    if (this.node.attr('typedef')) {
      this.keyword = 'typedef struct';
    } else {
      this.keyword = 'struct';
    }
  }

  Struct.prototype.render = function(container) {
    var id, isprot, item, k, name, t, templatetypes, _i, _len;
    item = $('<div class="item"/>');
    id = $('<span class="identifier"/>').text(this.name);
    k = $('<span class="keyword"/>');
    isprot = this.node.attr('access') === 'protected';
    if (isprot) k.append('protected ');
    k.append(this.keyword);
    name = $('<div/>').append(k).append(' ');
    name.attr('id', this.id);
    name.append(id);
    templatetypes = this.node.children('templatetypeparameter');
    if (templatetypes.length > 0) {
      name.append('&lt;');
      for (_i = 0, _len = templatetypes.length; _i < _len; _i++) {
        t = templatetypes[_i];
        t = $(t);
        name.append(t.attr('name'));
      }
      name.append('&gt;');
    }
    item.append(name);
    item.append(cldoc.Doc.either(this.node));
    if (this.ref) {
      item.append(cldoc.Page.know_more(this.ref));
    } else {
      this.render_fields(item);
      this.render_variables(item);
    }
    return container.append(item);
  };

  Struct.prototype.render_variables = function(item) {
    var container, variable, variables, _i, _len, _results;
    variables = this.node.children('variable');
    if (variables.length === 0) return;
    container = cldoc.Variable.render_container();
    item.append(container);
    _results = [];
    for (_i = 0, _len = variables.length; _i < _len; _i++) {
      variable = variables[_i];
      _results.push(new cldoc.Variable($(variable)).render(container));
    }
    return _results;
  };

  Struct.prototype.render_fields = function(item) {
    var container, field, fields, tp, _i, _len, _results;
    fields = this.node.children('field, union');
    if (fields.length === 0) return;
    container = cldoc.Field.render_container();
    item.append(container);
    _results = [];
    for (_i = 0, _len = fields.length; _i < _len; _i++) {
      field = fields[_i];
      field = $(field);
      tp = cldoc.Page.node_type(field);
      if (tp) {
        _results.push(new tp(field).render(container));
      } else {
        _results.push(void 0);
      }
    }
    return _results;
  };

  return Struct;

})(cldoc.Node);

cldoc.Node.types.struct = cldoc.Struct;

cldoc.Class = (function(_super) {

  __extends(Class, _super);

  Class.title = ['Class', 'Classes'];

  function Class(node) {
    this.node = node;
    Class.__super__.constructor.call(this, this.node);
    this.keyword = 'class';
  }

  return Class;

})(cldoc.Struct);

cldoc.Node.types['class'] = cldoc.Class;

cldoc.Node.types.classtemplate = cldoc.Class;

cldoc.Namespace = (function(_super) {

  __extends(Namespace, _super);

  Namespace.title = ['Namespace', 'Namespaces'];

  function Namespace(node) {
    this.node = node;
    Namespace.__super__.constructor.call(this, this.node);
  }

  Namespace.prototype.render = function(container) {
    var a, classes, cls, div, row, tb, _i, _len;
    div = $('<div class="item"/>');
    container.append(div);
    a = cldoc.Page.make_link(this.ref, this.name);
    a.attr('id', this.id);
    div.append(a);
    div.append(new cldoc.Doc(this.brief).render());
    classes = this.node.children('class,struct');
    if (classes.length > 0) {
      tb = $('<table class="namespace"/>');
      for (_i = 0, _len = classes.length; _i < _len; _i++) {
        cls = classes[_i];
        cls = $(cls);
        row = $('<tr/>');
        a = cldoc.Page.make_link(cls.attr('ref'), cls.attr('name'));
        row.append($('<td/>').append(a));
        row.append($('<td class="doc"/>').append(cldoc.Doc.either(cls)));
        tb.append(row);
      }
      return div.append(tb);
    }
  };

  return Namespace;

})(cldoc.Node);

cldoc.Node.types.namespace = cldoc.Namespace;

cldoc.Typedef = (function(_super) {

  __extends(Typedef, _super);

  Typedef.title = ['Typedef', 'Typedefs'];

  function Typedef(node) {
    this.node = node;
    Typedef.__super__.constructor.call(this, this.node);
  }

  Typedef.render_container = function() {
    return $('<table class="alt typedefs"/>');
  };

  Typedef.prototype.render = function(container) {
    var row, td;
    row = $('<tr class="typedef"/>');
    row.attr('id', this.id);
    row.append($('<td class="typedef_name identifier"/>').text(this.node.attr('name')));
    row.append($('<td class="typedef_decl keyword">type</td>'));
    row.append($('<td class="typedef_type"/>').append(new cldoc.Type(this.node.children('type')).render()));
    container.append(row);
    row = $('<tr class="doc"/>');
    td = $('<td colspan="3"/>').append(cldoc.Doc.either(this.node));
    row.append(td);
    return container.append(row);
  };

  return Typedef;

})(cldoc.Node);

cldoc.Node.types.typedef = cldoc.Typedef;

cldoc.Variable = (function(_super) {

  __extends(Variable, _super);

  Variable.title = ['Variable', 'Variables'];

  function Variable(node) {
    this.node = node;
    Variable.__super__.constructor.call(this, this.node);
  }

  Variable.render_container = function() {
    return $('<table class="variables"/>');
  };

  Variable.prototype.render = function(container) {
    var doctd, row;
    row = $('<tr/>');
    row.attr('id', this.node.attr('id'));
    row.append($('<td class="variable_name identifier"/>').text(this.node.attr('name')));
    row.append($('<td class="variable_type"/>').append(new cldoc.Type(this.node.children('type')).render()));
    doctd = $('<td class="doc"/>').appendTo(row);
    doctd.append(cldoc.Doc.either(this.node));
    return container.append(row);
  };

  return Variable;

})(cldoc.Node);

cldoc.Node.types.variable = cldoc.Variable;

cldoc.Function = (function(_super) {

  __extends(Function, _super);

  Function.title = ['Function', 'Functions'];

  function Function(node) {
    this.node = node;
    Function.__super__.constructor.call(this, this.node);
  }

  Function.prototype.render = function(container) {
    var arg, args, argtable, argtr, argtype, decldiv, div, doc, i, isover, isprot, isvirt, name, ov, override, overrides, ret, retdiv, retdoc, returntype, row, specs, table, td, tr, _ref2, _ref3, _results;
    div = $('<div class="function"/>').appendTo(container);
    decldiv = $('<div class="declaration"/>').appendTo(div);
    decldiv.attr('id', this.id);
    isvirt = this.node.attr('virtual');
    isprot = this.node.attr('access') === 'protected';
    if (isvirt || isprot) {
      specs = $('<ul class="specifiers"/>').appendTo(decldiv);
      if (isprot) specs.append($('<li class="protected">protected</li>'));
      if (isvirt) {
        isover = this.node.attr('override');
        if (isover) {
          specs.append($('<li class="override">override</li>'));
        } else {
          specs.append($('<li class="virtual">virtual</li>'));
        }
        if (this.node.attr('abstract')) {
          specs.append($('<li class="abstract">abstract</li>'));
        }
      }
    }
    ret = this.node.children('return');
    if (ret.length > 0) {
      retdiv = $('<div class="return_type"/>').appendTo(decldiv);
      returntype = ret.children('type');
      retdiv.append(new cldoc.Type(returntype).render());
    }
    table = $('<table class="declaration"/>').appendTo(decldiv);
    row = $('<tr/>').appendTo(table);
    td = $('<td class="identifier"/>').text(this.name).appendTo(row);
    $('<td class="open_paren"/>').text('(').appendTo(row);
    args = this.node.children('argument');
    argtable = $('<table class="arguments"/>');
    for (i = 0, _ref2 = args.length - 1; i <= _ref2; i += 1) {
      if (i !== 0) {
        row = $('<tr/>').appendTo(table);
        $('<td colspan="2"/>').appendTo(row);
      }
      arg = $(args[i]);
      doc = cldoc.Doc.either(arg);
      argtype = arg.children('type');
      $('<td class="argumen_type"/>').append(new cldoc.Type(argtype).render()).appendTo(row);
      name = arg.attr('name');
      if (i !== args.length - 1) name += ',';
      $('<td class="argument_name"/>').text(name).appendTo(row);
      argtr = $('<tr/>').appendTo(argtable);
      argtr.attr('id', arg.attr('id'));
      $('<td/>').text(arg.attr('name')).appendTo(argtr);
      $('<td/>').html(doc).appendTo(argtr);
    }
    if (args.length === 0) $('<td colspan="2"/>').appendTo(row);
    $('<td class="close_paren"/>').text(')').appendTo(row);
    cldoc.Doc.either(this.node).appendTo(div);
    argtable.appendTo(div);
    retdoc = cldoc.Doc.either(ret);
    if (retdoc.length > 0) {
      tr = $('<tr class="return"/>').appendTo(argtable);
      $('<td class="keyword">return</td>').appendTo(tr);
      $('<td/>').append(retdoc).appendTo(tr);
    }
    override = this.node.children('override');
    if (override.length > 0) {
      overrides = $('<div class="overrides"/>').append($('<span class="title">Overrides: </span>'));
      div.append(overrides);
      _results = [];
      for (i = 0, _ref3 = override.length - 1; 0 <= _ref3 ? i <= _ref3 : i >= _ref3; 0 <= _ref3 ? i++ : i--) {
        ov = $(override[i]);
        if (i !== 0) {
          if (i === override.length - 1) {
            overrides.append(' and ');
          } else {
            overrides.append(', ');
          }
        }
        _results.push(overrides.append(cldoc.Page.make_link(ov.attr('ref'), ov.attr('name'))));
      }
      return _results;
    }
  };

  return Function;

})(cldoc.Node);

cldoc.Node.types["function"] = cldoc.Function;

cldoc.Field = (function(_super) {

  __extends(Field, _super);

  Field.title = ['Field', 'Fields'];

  function Field(node) {
    this.node = node;
    Field.__super__.constructor.call(this, this.node);
  }

  Field.render_container = function() {
    return $('<table class="fields"/>');
  };

  Field.prototype.render = function(container) {
    var doctd, row;
    row = $('<tr/>');
    row.attr('id', this.node.attr('id'));
    row.append($('<td class="field_name identifier"/>').text(this.node.attr('name')));
    row.append($('<td class="field_type"/>').append(new cldoc.Type(this.node.children('type')).render()));
    doctd = $('<td class="doc"/>').appendTo(row);
    doctd.append(cldoc.Doc.either(this.node));
    return container.append(row);
  };

  return Field;

})(cldoc.Node);

cldoc.Node.types.field = cldoc.Field;

cldoc.Method = (function(_super) {

  __extends(Method, _super);

  Method.title = ['Method', 'Methods'];

  function Method(node) {
    this.node = node;
    Method.__super__.constructor.call(this, this.node);
  }

  return Method;

})(cldoc.Function);

cldoc.Node.types.method = cldoc.Method;

cldoc.Constructor = (function(_super) {

  __extends(Constructor, _super);

  Constructor.title = ['Constructor', 'Constructors'];

  function Constructor(node) {
    this.node = node;
    Constructor.__super__.constructor.call(this, this.node);
  }

  return Constructor;

})(cldoc.Method);

cldoc.Node.types.constructor = cldoc.Constructor;

cldoc.Destructor = (function(_super) {

  __extends(Destructor, _super);

  Destructor.title = ['Destructor', 'Destructors'];

  function Destructor(node) {
    this.node = node;
    Destructor.__super__.constructor.call(this, this.node);
  }

  return Destructor;

})(cldoc.Method);

cldoc.Node.types.destructor = cldoc.Destructor;

cldoc.Base = (function(_super) {

  __extends(Base, _super);

  Base.title = ['Base', 'Bases'];

  function Base(node) {
    this.node = node;
    Base.__super__.constructor.call(this, this.node);
    this.type = this.node.children('type');
    this.access = this.node.attr('access');
    this.name = this.type.attr('name');
    this.id = this.type.attr('ref');
  }

  Base.render_container = function() {
    return $('<table class="bases"/>');
  };

  Base.prototype.render = function(container) {
    var row, type;
    type = new cldoc.Type(this.type);
    row = $('<tr/>').appendTo(container);
    row.attr('id', this.id);
    $('<td class="keyword"/>').text(this.access).appendTo(row);
    $('<td/>').html(type.render()).appendTo(row);
    return $('<td/>').html(cldoc.Doc.brief(this.node)).appendTo(row);
  };

  return Base;

})(cldoc.Node);

cldoc.Node.types.base = cldoc.Base;

cldoc.Subclass = (function(_super) {

  __extends(Subclass, _super);

  Subclass.title = ['Subclass', 'Subclasses'];

  function Subclass(node) {
    this.node = node;
    Subclass.__super__.constructor.call(this, this.node);
    this.access = this.node.attr('access');
  }

  Subclass.render_container = function() {
    return $('<table class="subclasses"/>');
  };

  Subclass.prototype.render = function(container) {
    var row;
    row = $('<tr/>').appendTo(container);
    row.attr('id', this.id);
    $('<td class="keyword"/>').text(this.access).appendTo(row);
    $('<td/>').html(cldoc.Page.make_link(this.ref, this.name)).appendTo(row);
    return $('<td/>').html(cldoc.Doc.brief(this.node)).appendTo(row);
  };

  return Subclass;

})(cldoc.Node);

cldoc.Node.types.subclass = cldoc.Subclass;

cldoc.Coverage = (function(_super) {

  __extends(Coverage, _super);

  Coverage.title = ['Coverage', 'Coverage'];

  function Coverage(node) {
    this.node = node;
    Coverage.__super__.constructor.call(this, this.node);
  }

  Coverage.prototype.get_coverage = function(type) {
    var ret;
    ret = {
      documented: parseInt(type.attr('documented')),
      undocumented: parseInt(type.attr('undocumented'))
    };
    ret.total = ret.documented + ret.undocumented;
    ret.percentage = Math.round(100 * ret.documented / ret.total);
    return ret;
  };

  Coverage.prototype.render_sidebar_type = function(type, container) {
    var a, cov, li, tt, typename;
    typename = type.attr('name');
    cov = this.get_coverage(type);
    if (cov.documented === 0 && cov.undocumented === 0) return;
    tt = cov.documented + ' out of ' + cov.total + ' (' + cov.percentage + '%)';
    a = cldoc.Page.make_link(cldoc.Page.current_page + '#' + typename, typename);
    li = $('<li/>').appendTo(container);
    if (cov.undocumented === 0) {
      li.append($('<span class="bullet complete"/>').html('&#x2713;'));
    } else {
      li.append($('<span class="bullet incomplete"/>').html('&#10007;'));
    }
    return li.append(a).append($('<div class="brief"/>').text(tt));
  };

  Coverage.prototype.render_sidebar = function(container) {
    var type, types, _i, _len, _results;
    types = this.node.children('type');
    _results = [];
    for (_i = 0, _len = types.length; _i < _len; _i++) {
      type = types[_i];
      _results.push(this.render_sidebar_type($(type), container));
    }
    return _results;
  };

  Coverage.prototype.render_type = function(type, container) {
    var cov, h3, loc, row, t, typename, undoc, _i, _len, _ref2, _results;
    typename = type.attr('name');
    cov = this.get_coverage(type);
    if (cov.documented === 0 && cov.undocumented === 0) return;
    h3 = $('<h3/>').text(typename).append(' (' + cov.percentage + '%)').appendTo(container);
    h3.attr('id', typename);
    t = $('<table class="coverage"/>').appendTo(container);
    $('<tr/>').append($('<td>Documented:</td>')).append($('<td/>').text(cov.documented)).appendTo(t);
    $('<tr/>').append($('<td>Undocumented:</td>')).append($('<td/>').text(cov.undocumented)).appendTo(t);
    t = $('<table class="undocumented"/>').appendTo(container);
    _ref2 = type.children('undocumented');
    _results = [];
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      undoc = _ref2[_i];
      undoc = $(undoc);
      row = $('<tr/>').appendTo(t);
      $('<td/>').text(undoc.attr('id')).appendTo(row);
      _results.push((function() {
        var _j, _len2, _ref3, _results2;
        _ref3 = undoc.children('location');
        _results2 = [];
        for (_j = 0, _len2 = _ref3.length; _j < _len2; _j++) {
          loc = _ref3[_j];
          loc = $(loc);
          $('<td/>').text(loc.attr('file')).appendTo(row);
          $('<td/>').text(loc.attr('line') + ':' + loc.attr('column')).appendTo(row);
          _results2.push(row = $('<tr/>').append('<td/>').appendTo(t));
        }
        return _results2;
      })());
    }
    return _results;
  };

  Coverage.prototype.render = function(container) {
    var type, types, _i, _len, _results;
    types = this.node.children('type');
    _results = [];
    for (_i = 0, _len = types.length; _i < _len; _i++) {
      type = types[_i];
      _results.push(this.render_type($(type), container));
    }
    return _results;
  };

  return Coverage;

})(cldoc.Node);

cldoc.Node.types.coverage = cldoc.Coverage;

cldoc.Arguments = (function(_super) {

  __extends(Arguments, _super);

  Arguments.title = ['Arguments', 'Arguments'];

  function Arguments(node) {
    this.node = node;
    Arguments.__super__.constructor.call(this, this.node);
  }

  Arguments.prototype.render_sidebar_function = function(func, container) {
    var a;
    a = cldoc.Page.make_link(cldoc.Page.current_page + '#' + func.attr('id'), func.attr('name'));
    return $('<li/>').html(a).appendTo(container);
  };

  Arguments.prototype.render_sidebar = function(container) {
    var f, funcs, _i, _len, _results;
    funcs = this.node.children('function');
    _results = [];
    for (_i = 0, _len = funcs.length; _i < _len; _i++) {
      f = funcs[_i];
      _results.push(this.render_sidebar_function($(f), container));
    }
    return _results;
  };

  Arguments.prototype.render_function = function(func, container) {
    var loc, misspelled, row, undocumented, x, _i, _len, _ref2;
    row = $('<tr class="title"/>').append($('<td class="identifier"/>').text(func.attr('name'))).appendTo(container);
    row.attr('id', func.attr('id'));
    _ref2 = func.children('location');
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      loc = _ref2[_i];
      loc = $(loc);
      $('<td/>').text(loc.attr('file')).appendTo(row);
      $('<td/>').text(loc.attr('line') + ':' + loc.attr('column')).appendTo(row);
      row = $('<tr/>').append('<td/>').appendTo(container);
    }
    undocumented = func.children('undocumented');
    if (undocumented.length > 0) {
      row = $('<tr class="undocumented"/>').append($('<td/>').text('Undocumented arguments:')).append($('<td colspan="2"/>').html(((function() {
        var _j, _len2, _results;
        _results = [];
        for (_j = 0, _len2 = undocumented.length; _j < _len2; _j++) {
          x = undocumented[_j];
          _results.push($(x).attr('name'));
        }
        return _results;
      })()).join(', '))).appendTo(container);
    }
    misspelled = func.children('misspelled');
    if (misspelled.length > 0) {
      row = $('<tr class="misspelled"/>').append($('<td/>').text('Misspelled arguments:')).append($('<td colspan="2"/>').html(((function() {
        var _j, _len2, _results;
        _results = [];
        for (_j = 0, _len2 = misspelled.length; _j < _len2; _j++) {
          x = misspelled[_j];
          _results.push($(x).attr('name'));
        }
        return _results;
      })()).join(', '))).appendTo(container);
    }
    if (func.children('undocumented-return')) {
      row = $('<tr class="undocumented"/>').append($('<td colspan="3"/>').text('Undocumented return value')).appendTo(container);
    }
    return row.addClass('last');
  };

  Arguments.prototype.render = function(container) {
    var f, funcs, t, _i, _len, _results;
    funcs = this.node.children('function');
    t = $('<table class="function"/>').appendTo(container);
    _results = [];
    for (_i = 0, _len = funcs.length; _i < _len; _i++) {
      f = funcs[_i];
      _results.push(this.render_function($(f), t));
    }
    return _results;
  };

  return Arguments;

})(cldoc.Node);

cldoc.Node.types.arguments = cldoc.Arguments;

cldoc.Report = (function(_super) {

  __extends(Report, _super);

  Report.title = ['Report', 'Report'];

  function Report(node) {
    this.node = node;
    Report.__super__.constructor.call(this, this.node);
  }

  Report.prototype.render_sidebar = function(container) {
    return container.append($('<li/>').append(cldoc.Page.make_link(this.ref, this.name)));
  };

  Report.prototype.render = function(container) {};

  return Report;

})(cldoc.Node);

cldoc.Node.types.report = cldoc.Report;

cldoc.References = (function(_super) {

  __extends(References, _super);

  References.title = ['References', 'References'];

  function References(node) {
    this.node = node;
    References.__super__.constructor.call(this, this.node);
  }

  References.prototype.render_sidebar = function(container) {
    var a, child, _i, _len, _ref2, _results;
    _ref2 = this.node.children();
    _results = [];
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      child = _ref2[_i];
      child = $(child);
      a = cldoc.Page.make_link(cldoc.Page.current_page + '#ref-' + child.attr('id'), child.attr('name'));
      _results.push($('<li/>').append($('<span class="keyword"/>').text(cldoc.tag(child)[0])).append(' ').append(a).appendTo(container));
    }
    return _results;
  };

  References.render_container = function() {
    return $('<table class="references"/>');
  };

  References.prototype.render = function(container) {
    var child, component, id, kw, loc, name, refs, row, tp, x, _i, _j, _k, _len, _len2, _len3, _ref2, _ref3, _ref4, _results;
    _ref2 = this.node.children();
    _results = [];
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      child = _ref2[_i];
      child = $(child);
      kw = $('<span class="keyword"/>').text(cldoc.tag(child)[0]).append('&nbsp;');
      id = $('<span class="identifier"/>').text(child.attr('id'));
      row = $('<tr/>').append($('<td class="title"/>').append(kw).append(id)).appendTo(container);
      row.attr('id', 'ref-' + child.attr('id'));
      _ref3 = child.children('location');
      for (_j = 0, _len2 = _ref3.length; _j < _len2; _j++) {
        loc = _ref3[_j];
        loc = $(loc);
        $('<td/>').text(loc.attr('file')).appendTo(row);
        $('<td/>').text(loc.attr('line') + ':' + loc.attr('column')).appendTo(row);
        row = $('<tr/>').append('<td/>').appendTo(container);
      }
      _ref4 = child.children('doctype');
      for (_k = 0, _len3 = _ref4.length; _k < _len3; _k++) {
        tp = _ref4[_k];
        tp = $(tp);
        name = tp.attr('name');
        component = tp.attr('component');
        if (component) name = name + '.' + component;
        refs = ((function() {
          var _l, _len4, _ref5, _results2;
          _ref5 = tp.children('ref');
          _results2 = [];
          for (_l = 0, _len4 = _ref5.length; _l < _len4; _l++) {
            x = _ref5[_l];
            _results2.push($(x).attr('name'));
          }
          return _results2;
        })()).join(', ');
        row = $('<tr class="missing"/>').append($('<td/>').text(name)).append($('<td/>').text(refs)).append('<td/>').appendTo(container);
      }
      _results.push(row.addClass('last'));
    }
    return _results;
  };

  return References;

})(cldoc.Node);

cldoc.Node.types.references = cldoc.References;

cldoc.Union = (function(_super) {

  __extends(Union, _super);

  Union.title = ['Union', 'Unions'];

  function Union(node) {
    this.node = node;
    Union.__super__.constructor.call(this, this.node);
  }

  Union.render_container = function() {
    return $('<table class="fields"/>');
  };

  Union.prototype.sidebar_name = function() {
    return $('<span><span class="keyword">union</span></span>').text(this.name);
  };

  Union.prototype.render = function(container) {
    var child, ctable, doctd, kw, row, td, tp, _i, _len, _ref2, _results;
    row = $('<tr class="union"/>').appendTo(container);
    kw = $('<span class="keyword">union</span>');
    $('<td/>').append(kw).appendTo(row);
    $('<td/>').appendTo(row);
    doctd = $('<td class="doc"/>').appendTo(row);
    doctd.append(cldoc.Doc.either(this.node));
    ctable = $('<table class="fields union"/>');
    row = $('<tr/>').appendTo(container);
    td = $('<td colspan="3"/>').appendTo(row).append(ctable);
    _ref2 = this.node.children();
    _results = [];
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      child = _ref2[_i];
      child = $(child);
      tp = cldoc.Page.node_type(child);
      if (tp) {
        _results.push(new tp(child).render(ctable));
      } else {
        _results.push(void 0);
      }
    }
    return _results;
  };

  return Union;

})(cldoc.Node);

cldoc.Node.types.union = cldoc.Union;
