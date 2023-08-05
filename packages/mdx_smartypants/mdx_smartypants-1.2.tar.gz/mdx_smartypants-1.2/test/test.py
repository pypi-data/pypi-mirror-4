
import markdown
# import mdx_smartypants

def test_smartypants():
    
    text = """
Markdown makes HTML from simple text files. But--it lacks typographic
"prettification." That... That'd be sweet. Definitely 7---8 on a '10-point
scale'. Now it has it.

Huzzah!
"""

    answer = """
<p>Markdown makes HTML from simple text files. But&mdash;it lacks typographic
&ldquo;prettification.&rdquo; That&hellip; That&rsquo;d be sweet. Definitely 7&ndash;8 on a &lsquo;10-point
scale&rsquo;. Now it has it.</p>
<p>Huzzah!</p>
"""
    result = markdown.markdown(text, extensions=['smartypants'])
   
    assert result.strip() == answer.strip()


def test_code():
    md = """
This is a "paragraph." It should have--nay, needs, typographic pretties.

    def something(a):
        "I am a doc string. I should not be curled"
        print a + ", huh?"  # i am code -- not em-dash safe

and this is not code. So...make me pretty!
"""

    result = markdown.markdown(md, extensions=['smartypants'])
    
    answer = """
<p>This is a &ldquo;paragraph.&rdquo; It should have&mdash;nay, needs, typographic pretties.</p>
<pre><code>def something(a):
    "I am a doc string. I should not be curled"
    print a + ", huh?"  # i am code -- not em-dash safe
</code></pre>
<p>and this is not code. So&hellip;make me pretty!</p>
"""
    
    assert result.strip() == answer.strip()

