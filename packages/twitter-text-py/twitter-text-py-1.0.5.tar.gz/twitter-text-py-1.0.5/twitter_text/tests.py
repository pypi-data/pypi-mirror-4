# encoding=utf-8

import twitter_text
from twitter_text.unicode import force_unicode

text = force_unicode('@foo said the funniest thing to ＠monkeybat and @bar http://dryan.net/xxxxx?param=true#hash #comedy #url')
tt = twitter_text.TwitterText(text)

def autolink_tests(tests, passed, failed):
    print u'Running Autolink tests'

    correct_auto_link = u'<a class="tweet-url username" href="http://twitter.com/foo" rel="nofollow">@foo</a> said the funniest thing to <a class="tweet-url username" href="http://twitter.com/monkeybat" rel="nofollow">＠monkeybat</a> and <a class="tweet-url username" href="http://twitter.com/bar" rel="nofollow">@bar</a> <a href="http://dryan.net/xxxxx?param=true#hash" rel="nofollow">http://dryan.net/xxxxx?param=t…</a> <a href="http://twitter.com/search?q=%23comedy" title="#comedy" class="tweet-url hashtag" rel="nofollow">#comedy</a> <a href="http://twitter.com/search?q=%23url" title="#url" class="tweet-url hashtag" rel="nofollow">#url</a>'
    correct_auto_link_with_hit_highlight = u'<a class="tweet-url username" href="http://twitter.com/foo" rel="nofollow">@foo</a> said the <em class="search-hit">funniest</em> thing to <a class="tweet-url username" href="http://twitter.com/monkeybat" rel="nofollow">＠monkeybat</a> and <a class="tweet-url username" href="http://twitter.com/bar" rel="nofollow">@bar</a> <a href="http://dryan.net/xxxxx?param=true#hash" rel="nofollow">http://dryan.net/xxxxx?param=t…</a> <a href="http://twitter.com/search?q=%23comedy" title="#comedy" class="tweet-url hashtag" rel="nofollow">#comedy</a> <a href="http://twitter.com/search?q=%23url" title="#url" class="tweet-url hashtag" rel="nofollow">#url</a>'
    correct_auto_link_usernames_or_lists = u'<a class="tweet-url username" href="http://twitter.com/foo" rel="nofollow">@foo</a> said the funniest thing to <a class="tweet-url username" href="http://twitter.com/monkeybat" rel="nofollow">＠monkeybat</a> and <a class="tweet-url username" href="http://twitter.com/bar" rel="nofollow">@bar</a> http://dryan.net/xxxxx?param=true#hash #comedy #url'
    correct_auto_link_hashtags = u'@foo said the funniest thing to ＠monkeybat and @bar http://dryan.net/xxxxx?param=true#hash <a href="http://twitter.com/search?q=%23comedy" title="#comedy" class="tweet-url hashtag" rel="nofollow">#comedy</a> <a href="http://twitter.com/search?q=%23url" title="#url" class="tweet-url hashtag" rel="nofollow">#url</a>'
    correct_auto_link_urls_custom = u'@foo said the funniest thing to ＠monkeybat and @bar <a href="http://dryan.net/xxxxx?param=true#hash" rel="nofollow">http://dryan.net/xxxxx?param=t…</a> #comedy #url'
    correct_auto_link_urls_custom_with_kwargs = u'@foo said the funniest thing to ＠monkeybat and @bar <a href="http://dryan.net/xxxxx?param=true#hash" class="boosh" rel="external" title="a link">http://dryan.net/xxxxx?param=t…</a> #comedy #url'

    autolink = twitter_text.Autolink(text)

    # test the overall auto_link method
    test_autolink = tt.autolink.auto_link()
    if test_autolink == correct_auto_link_with_hit_highlight:
        print u'\033[92m  Attached auto_link passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached auto_link failed:\033[0m'
        print u'    Expected: %s' % correct_auto_link_with_hit_highlight
        print u'    Returned: %s' % test_autolink
        failed +=1
    tests +=1

    test_autolink = autolink.auto_link()
    if test_autolink == correct_auto_link:
        print u'\033[92m  Stand alone auto_link passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone auto_link failed:\033[0m'
        print u'    Expected: %s' % correct_auto_link
        print u'    Returned: %s' % test_autolink
        failed +=1
    tests +=1
    
    if failed > 0: # we need to run the individual methods to determine what failed
        # test the auto_link_usernames_or_lists method
        this_tt = twitter_text.TwitterText(text)
        autolink = twitter_text.Autolink(text)
        
        test_autolink = this_tt.autolink.auto_link_usernames_or_lists()
        if test_autolink == correct_auto_link_usernames_or_lists:
            print u'\033[92m  Attached auto_link_usernames_or_lists passed\033[0m'
            passed += 1
        else:
            print u'\033[91m  Attached auto_link_usernames_or_lists failed:\033[0m'
            print u'    Expected: %s' % correct_auto_link_usernames_or_lists
            print u'    Returned: %s' % test_autolink
            failed +=1
        tests +=1

        test_autolink = autolink.auto_link_usernames_or_lists()
        if test_autolink == correct_auto_link_usernames_or_lists:
            print u'\033[92m  Stand alone auto_link_usernames_or_lists passed\033[0m'
            passed += 1
        else:
            print u'\033[91m  Stand alone auto_link_usernames_or_lists failed:\033[0m'
            print u'    Expected: %s' % correct_auto_link_usernames_or_lists
            print u'    Returned: %s' % test_autolink
            failed +=1
        tests +=1
        
        # test the auto_link_hashtags method
        this_tt = twitter_text.TwitterText(text)
        autolink = twitter_text.Autolink(text)
        
        test_autolink = this_tt.autolink.auto_link_hashtags()
        if test_autolink == correct_auto_link_hashtags:
            print u'\033[92m  Attached auto_link_hashtags passed\033[0m'
            passed += 1
        else:
            print u'\033[91m  Attached auto_link_hashtags failed:\033[0m'
            print u'    Expected: %s' % correct_auto_link_hashtags
            print u'    Returned: %s' % test_autolink
            failed +=1
        tests +=1

        test_autolink = autolink.auto_link_hashtags()
        if test_autolink == correct_auto_link_hashtags:
            print u'\033[92m  Stand alone auto_link_hashtags passed\033[0m'
            passed += 1
        else:
            print u'\033[91m  Stand alone auto_link_hashtags failed:\033[0m'
            print u'    Expected: %s' % correct_auto_link_hashtags
            print u'    Returned: %s' % test_autolink
            failed +=1
        tests +=1

        # test the auto_link_urls_custom
        this_tt = twitter_text.TwitterText(text)
        autolink = twitter_text.Autolink(text)
        
        test_autolink = this_tt.autolink.auto_link_urls_custom()
        if test_autolink == correct_auto_link_urls_custom:
            print u'\033[92m  Attached auto_link_urls_custom passed\033[0m'
            passed += 1
        else:
            print u'\033[91m  Attached auto_link_urls_custom failed:\033[0m'
            print u'    Expected: %s' % correct_auto_link_urls_custom
            print u'    Returned: %s' % test_autolink
            failed +=1
        tests +=1

        test_autolink = autolink.auto_link_urls_custom()
        if test_autolink == correct_auto_link_urls_custom:
            print u'\033[92m  Stand alone auto_link_urls_custom passed\033[0m'
            passed += 1
        else:
            print u'\033[91m  Stand alone auto_link_urls_custom failed:\033[0m'
            print u'    Expected: %s' % correct_auto_link_urls_custom
            print u'    Returned: %s' % test_autolink
            failed +=1
        tests +=1
        
    # test the auto_link_urls_custom with some kwargs for HTML attrs
    this_tt = twitter_text.TwitterText(text)
    autolink = twitter_text.Autolink(text)
    
    test_autolink = this_tt.autolink.auto_link_urls_custom(rel = 'external', class_name = 'boosh', title = 'a link')
    if test_autolink == correct_auto_link_urls_custom_with_kwargs:
        print u'\033[92m  Attached auto_link_urls_custom with kwargs passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached auto_link_urls_custom with kwargs failed:\033[0m'
        print u'    Expected: %s' % correct_auto_link_urls_custom_with_kwargs
        print u'    Returned: %s' % test_autolink
        failed +=1
    tests +=1

    test_autolink = autolink.auto_link_urls_custom(rel = 'external', class_name = 'boosh', title = 'a link')
    if test_autolink == correct_auto_link_urls_custom_with_kwargs:
        print u'\033[92m  Stand alone auto_link_urls_custom with kwargs passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone auto_link_urls_custom with kwargs failed:\033[0m'
        print u'    Expected: %s' % correct_auto_link_urls_custom_with_kwargs
        print u'    Returned: %s' % test_autolink
        failed +=1
    tests +=1


    return tests, passed, failed

def extractor_tests(tests, passed, failed):
    print u'Running Extractor tests'

    correct_mentioned_screen_names = [u'foo', u'monkeybat', u'bar']
    correct_mentioned_screen_names_with_indices = [{'indices': (0, 4), 'screen_name': u'foo'}, {'indices': (32, 42), 'screen_name': u'monkeybat'}, {'indices': (47, 51), 'screen_name': u'bar'}]
    correct_reply_screen_name = 'foo'
    correct_urls = [u'http://dryan.net/xxxxx?param=true#hash']
    correct_urls_with_indices = [{'url': u'http://dryan.net/xxxxx?param=true#hash', 'indices': (52, 90)}]
    correct_hashtags = [u'comedy', u'url']
    correct_hashtags_with_indices = [{'indices': (91, 98), 'hashtag': u'comedy'}, {'indices': (99, 103), 'hashtag': u'url'}]

    extractor = twitter_text.Extractor(text)
    
    if tt.extractor.extract_mentioned_screen_names() == correct_mentioned_screen_names:
        print u'\033[92m  Attached extract_mentioned_screen_names passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached extract_mentioned_screen_names failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_mentioned_screen_names)
        print u'    Returned: %s' % force_unicode(tt.extractor.extract_mentioned_screen_names())
        failed +=1
    tests +=1

    if extractor.extract_mentioned_screen_names() == correct_mentioned_screen_names:
        print u'\033[92m  Stand alone extract_mentioned_screen_names passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone extract_mentioned_screen_names failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_mentioned_screen_names)
        print u'    Returned: %s' % force_unicode(extractor.extract_mentioned_screen_names())
        failed +=1
    tests +=1

    if tt.extractor.extract_mentioned_screen_names_with_indices() == correct_mentioned_screen_names_with_indices:
        print u'\033[92m  Attached extract_mentioned_screen_names_with_indices passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached extract_mentioned_screen_names_with_indices failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_mentioned_screen_names_with_indices)
        print u'    Returned: %s' % force_unicode(tt.extractor.extract_mentioned_screen_names_with_indices())
        failed += 1
    tests += 1

    if extractor.extract_mentioned_screen_names_with_indices() == correct_mentioned_screen_names_with_indices:
        print u'\033[92m  Stand alone extract_mentioned_screen_names_with_indices passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone extract_mentioned_screen_names_with_indices failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_mentioned_screen_names_with_indices)
        print u'    Returned: %s' % force_unicode(extractor.extract_mentioned_screen_names_with_indices())
        failed += 1
    tests += 1

    if tt.extractor.extract_reply_screen_name() == correct_reply_screen_name:
        print u'\033[92m  Attached extract_reply_screen_name passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached extract_reply_screen_name failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_reply_screen_name)
        print u'    Returned: %s' % force_unicode(tt.extractor.extract_reply_screen_name())
        failed +=1
    tests +=1

    if extractor.extract_reply_screen_name() == correct_reply_screen_name:
        print u'\033[92m  Stand alone extract_reply_screen_name passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone extract_reply_screen_name failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_reply_screen_name)
        print u'    Returned: %s' % force_unicode(extractor.extract_reply_screen_name())
        failed +=1
    tests +=1

    if tt.extractor.extract_urls() == correct_urls:
        print u'\033[92m  Attached extract_urls passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached extract_urls failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_urls)
        print u'    Returned: %s' % force_unicode(tt.extractor.extract_urls())
        failed +=1
    tests +=1

    if extractor.extract_urls() == correct_urls:
        print u'\033[92m  Stand alone extract_urls passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone extract_urls failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_urls)
        print u'    Returned: %s' % force_unicode(extractor.extract_urls())
        failed +=1
    tests +=1

    if tt.extractor.extract_urls_with_indices() == correct_urls_with_indices:
        print u'\033[92m  Attached extract_urls_with_indices passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached extract_urls_with_indices failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_urls_with_indices)
        print u'    Returned: %s' % force_unicode(tt.extractor.extract_urls_with_indices())
        failed += 1
    tests += 1

    if extractor.extract_urls_with_indices() == correct_urls_with_indices:
        print u'\033[92m  Stand alone extract_urls_with_indices passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone extract_urls_with_indices failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_urls_with_indices)
        print u'    Returned: %s' % force_unicode(extractor.extract_urls_with_indices())
        failed += 1
    tests += 1

    if tt.extractor.extract_hashtags() == correct_hashtags:
        print u'\033[92m  Attached extract_hashtags passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached extract_hashtags failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_hashtags)
        print u'    Returned: %s' % force_unicode(tt.extractor.extract_hashtags())
        failed +=1
    tests +=1

    if extractor.extract_hashtags() == correct_hashtags:
        print u'\033[92m  Stand alone extract_hashtags passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone extract_hashtags failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_hashtags)
        print u'    Returned: %s' % force_unicode(extractor.extract_hashtags())
        failed +=1
    tests +=1

    if tt.extractor.extract_hashtags_with_indices() == correct_hashtags_with_indices:
        print u'\033[92m  Attached extract_hashtags_with_indices passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached extract_hashtags_with_indices failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_hashtags_with_indices)
        print u'    Returned: %s' % force_unicode(tt.extractor.extract_hashtags_with_indices())
        failed += 1
    tests += 1
        
    if extractor.extract_hashtags_with_indices() == correct_hashtags_with_indices:
        print u'\033[92m  Stand alone extract_hashtags_with_indices passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone extract_hashtags_with_indices failed:\033[0m'
        print u'    Expected: %s' % force_unicode(correct_hashtags_with_indices)
        print u'    Returned: %s' % force_unicode(extractor.extract_hashtags_with_indices())
        failed += 1
    tests += 1
    
    return tests, passed, failed
    
def highlighter_tests(tests, passed, failed):
    print u'Running HitHighlighter tests'
    
    correct_hit_highlight = u'@foo said the <em class="search-hit">funniest</em> thing to ＠monkeybat and @bar http://dryan.net/xxxxx?param=true#hash #comedy #url'
    
    highlighter = twitter_text.HitHighlighter(text)

    test_highlight = tt.highlighter.hit_highlight('funniest')
    if test_highlight == correct_hit_highlight:
        print u'\033[92m  Attached hit_highlight passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached hit_highlight failed:\033[0m'
        print u'    Expected: %s' % correct_hit_highlight
        print u'    Returned: %s' % test_highlight
        failed += 1
    tests += 1
        
    test_highlight = highlighter.hit_highlight('funniest')
    if test_highlight == correct_hit_highlight:
        print u'\033[92m  Stand alone hit_highlight passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone hit_highlight failed:\033[0m'
        print u'    Expected: %s' % correct_hit_highlight
        print u'    Returned: %s' % test_highlight
        failed += 1
    tests += 1
    
    return tests, passed, failed
    
def validation_tests(tests, passed, failed):
    print u'Running Validation tests'
    
    validation = twitter_text.Validation(text)
    
    if tt.validation.tweet_length() == len(text):
        print u'\033[92m  Attached tweet_length passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached tweet_length failed:\033[0m'
        print u'    Expected: %d' % len(text)
        print u'    Returned: %d' % tt.validation.tweet_length()
        failed += 1
    tests += 1

    if validation.tweet_length() == len(text):
        print u'\033[92m  Stand alone tweet_length passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone tweet_length failed:\033[0m'
        print u'    Expected: %d' % len(text)
        print u'    Returned: %d' % validation.tweet_length()
        failed += 1
    tests += 1

    if tt.validation.tweet_invalid() == (False, None):
        print u'\033[92m  Attached tweet_invalid passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Attached tweet_invalid failed:\033[0m'
        print u'    Expected: %s' % 'False, None'
        print u'    Returned: %s, %s' % tt.validation.tweet_invalid()
        failed += 1
    tests += 1

    if validation.tweet_invalid() == (False, None):
        print u'\033[92m  Stand alone tweet_invalid passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Stand alone tweet_invalid failed:\033[0m'
        print u'    Expected: %s' % 'False, None'
        print u'    Returned: %s, %s' % validation.tweet_invalid()
        failed += 1
    tests += 1
    
    print ''
    print u'Running Validation tests on bad text'
    bad_tweets = {
        'empty': u'',
        'too_long': text + text,
        'invalid_characters': text
    }
    
    this_tt = twitter_text.TwitterText(bad_tweets['empty'])
    if this_tt.validation.tweet_invalid() == (True, 'Empty text'):
        print u'\033[92m  Empty Text tweet_invalid passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Empty Text tweet_invalid failed:\033[0m'
        print u'    Expected: %s' % 'True, Empty text'
        print u'    Returned: %s, %s' % validation.tweet_invalid()
        failed += 1
    tests += 1
        
    this_tt = twitter_text.TwitterText(bad_tweets['too_long'])
    if this_tt.validation.tweet_invalid() == (True, 'Too long'):
        print u'\033[92m  Too Long tweet_invalid passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Too Long tweet_invalid failed:\033[0m'
        print u'    Expected: %s' % 'True, Too long'
        print u'    Returned: %s, %s' % validation.tweet_invalid()
        failed += 1
    tests += 1
    
    missed_bad_characters = []
    for bad_character in validation.INVALID_CHARACTERS:
        this_text = force_unicode(bad_tweets['invalid_characters'] + bad_character)
        this_tt = twitter_text.TwitterText(this_text)
        if not this_tt.validation.tweet_invalid() == (True, 'Invalid characters'):
            missed_bad_characters.append(bad_character)
    if not len(missed_bad_characters):
        print u'\033[92m  Invalid Characters tweet_invalid passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Invalid Characters tweet_invalid failed:\033[0m'
        print u'    Expected: %s' % '[]'
        print u'    Returned: %s' % force_unicode(missed_bad_characters)
        failed += 1
    tests += 1
    
    return tests, passed, failed
    
def templatetag_tests(tests, passed, failed):
    print u'Running Django templatetag tests'
    from twitter_text.templatetags import twitterize

    correct_auto_link = u'<a class="tweet-url username" href="http://twitter.com/foo" rel="nofollow">@foo</a> said the funniest thing to <a class="tweet-url username" href="http://twitter.com/monkeybat" rel="nofollow">＠monkeybat</a> and <a class="tweet-url username" href="http://twitter.com/bar" rel="nofollow">@bar</a> <a href="http://dryan.net/xxxxx?param=true#hash" rel="nofollow">http://dryan.net/xxxxx?param=t…</a> <a href="http://twitter.com/search?q=%23comedy" title="#comedy" class="tweet-url hashtag" rel="nofollow">#comedy</a> <a href="http://twitter.com/search?q=%23url" title="#url" class="tweet-url hashtag" rel="nofollow">#url</a>'
    correct_auto_link_with_hit_highlight = u'<a class="tweet-url username" href="http://twitter.com/foo" rel="nofollow">@foo</a> said the <em class="search-hit">funniest</em> thing to <a class="tweet-url username" href="http://twitter.com/monkeybat" rel="nofollow">＠monkeybat</a> and <a class="tweet-url username" href="http://twitter.com/bar" rel="nofollow">@bar</a> <a href="http://dryan.net/xxxxx?param=true#hash" rel="nofollow">http://dryan.net/xxxxx?param=t…</a> <a href="http://twitter.com/search?q=%23comedy" title="#comedy" class="tweet-url hashtag" rel="nofollow">#comedy</a> <a href="http://twitter.com/search?q=%23url" title="#url" class="tweet-url hashtag" rel="nofollow">#url</a>'
    
    if twitterize.twitter_text(text) == correct_auto_link:
        print u'\033[92m  Django templatetag with no search term passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Django templatetag with no search term failed:\033[0m'
        print u'    Expected: %s' % correct_auto_link
        print u'    Returned: %s' % twitterize.twitter_text(text)
        failed += 1
    tests += 1

    if twitterize.twitter_text(text, 'funniest') == correct_auto_link_with_hit_highlight:
        print u'\033[92m  Django templatetag with search term passed\033[0m'
        passed += 1
    else:
        print u'\033[91m  Django templatetag with search term failed:\033[0m'
        print u'    Expected: %s' % correct_auto_link_with_hit_highlight
        print u'    Returned: %s' % twitterize.twitter_text(text, 'funniest')
        failed += 1
    tests += 1
    
    return tests, passed, failed

def run_all():
    tests, passed, failed = 0, 0, 0

    tests, passed, failed = validation_tests(tests, passed, failed)

    print ''
    tests, passed, failed = extractor_tests(tests, passed, failed)

    print ''
    tests, passed, failed = highlighter_tests(tests, passed, failed)

    print ''
    tests, passed, failed = autolink_tests(tests, passed, failed)

    print ''
    tests, passed, failed = templatetag_tests(tests, passed, failed)

    print ''
    print u'Checking hit_highlight assertion that text does not have HTML tags already present'
    try:
        tt.highlighter.hit_highlight('funniest')
        print u'\033[91m  hit_highlight HTML tag check failed\033[0m'
        failed += 1
    except AssertionError:
        print u'\033[92m  hit_highlight HTML tag check passed\033[0m'
        passed += 1
    tests += 1

    results = u'%d tests run. \033[92m%d passed.\033[0m' % (tests, passed)
    if failed > 0:
        results = u'%s \033[91m%d failed.\033[0m' % (results, failed)
    print ''
    print u'\033[1m%s\033[0;0m' % results
        
if __name__ == '__main__':
    run_all()