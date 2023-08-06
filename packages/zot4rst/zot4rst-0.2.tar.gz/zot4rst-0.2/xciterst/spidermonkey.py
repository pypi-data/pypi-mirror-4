import xciterst
import spidermonkey
import json
import os.path

class Citeproc(xciterst.CiteprocWrapper):
    def js_path(self, p):
        return os.path.join(os.path.dirname(__file__), 'js', p)

    def js_exec(self, p):
        return self.context.execute(open(self.js_path(p)).read())

    def __init__(self):
        rt = spidermonkey.Runtime()
        self.context = rt.new_context()
        
        self.js_exec('xmle4x.js')
        self.js_exec('citeproc.js')

        locale = open("../citeproc-js/locale/locales-en-US.xml").read()
        localeJSON = json.dumps(locale,ensure_ascii=False)
        self.context.execute('locale_en = %s;' % localeJSON)

        self.js_exec('sys.js')
        self.js_exec("abbreviations.js")

        # Unneeded in this context
        #self.context.execute('styleName = \"%s\";' % name)

        # Pull in csl through format declaration
        #csl = open('../mlz-styles/mlz-%s.csl' % name).read()
        #cslJSON = json.dumps(csl,ensure_ascii=False)
        #self.context.execute('csl = %s;' % cslJSON)

        # Instantiate engine through set format declaration
        #self.context.execute('sys = new MySys();')
        #self.context.execute('citeproc = new CSL.Engine(sys,csl);')

        # Use explicit bibliography loading
        #itemsJSON = open('./json/items.json' % name).read()
        #self.context.execute('citeproc.sys._cache = %s;' % itemsJSON)

        

        cite = [""];
        self.context.add_global("cite", cite)
        monitor = [""];
        self.context.add_global("monitor", monitor)
        
        self.is_in_text_style = self.context.execute("('in-text' === citeproc.opt.xclass);");

    def citeproc_update_items(self, ids):
        """Call updateItems in citeproc."""
        return self.context.execute("citeproc.updateItems(%s)" % json.dumps(ids))

    def citeproc_make_bibliography(self):
        """Call makeBibliography in citeproc. Should return an HTML string."""
        pass

    def citeproc_append_citation_cluster_batch(self, clusters):
        """Call appendCitationCluster for a batch of citations."""
        pass




    def instantiateCiteProc(self, format):
        m = re.match(".*/(?:mlz-)*(.*)(?:\.csl)*$", format)
        if m:
            format = m.group(1)
        csl = open('../mlz-styles/mlz-%s.csl' % format).read()
        cslJSON = json.dumps(csl,ensure_ascii=False)
        self.context.execute('csl = %s;' % cslJSON)

        self.context.execute('sys = new MySys();')
        self.context.execute('citeproc = new CSL.Engine(sys,csl);')

        support = open('./js/citeproc-support.js').read()
        self.context.execute(support)
        # For debugging -- allows print() to be used in citeproc.js
        def printme (txt):
            print txt
        self.context.add_global("print", printme)
