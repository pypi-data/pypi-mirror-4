/*
 * jquery.socialshareprivacy.js | 2 Klicks fuer mehr Datenschutz
 *
 * http://www.heise.de/extras/socialshareprivacy/
 * http://www.heise.de/ct/artikel/2-Klicks-fuer-mehr-Datenschutz-1333879.html
 *
 * Copyright (c) 2011 Hilko Holweg, Sebastian Hilbig, Nicolas Heiringhoff, Juergen Schmidt,
 * Heise Zeitschriften Verlag GmbH & Co. KG, http://www.heise.de
 *
 * is released under the MIT License http://www.opensource.org/licenses/mit-license.php
 *
 * Spread the word, link to us if you can.
 */
(function ($) {

    "use strict";

    /*
     * helper functions
     */

    // abbreviate at last blank before length and add "\u2026" (horizontal ellipsis)
    function abbreviateText(text, length) {
        var abbreviated = text;
        if (abbreviated.length <= length) {
            return text;
        }

        var lastWhitespaceIndex = abbreviated.substring(0, length - 1).lastIndexOf(' ');
        abbreviated = abbreviated.substring(0, lastWhitespaceIndex) + "…";

        return abbreviated;
    }

    // returns content of <meta name="" content=""> tags or '' if empty/non existant
    function getMeta(name) {
        var metaContent = $('meta[name="' + name + '"]').attr('content');
        return metaContent || '';
    }

    // create tweet text from content of <meta name="DC.description">,
    // or <meta name="DC.title"> and <meta name="DC.creator">,
    // fallback to content of <title> tag
    function getTweetText() {
        var text = '';
        var description = $.trim(getMeta('DC.description') || getMeta('description'));
        var title = $.trim(getMeta('DC.title') || $('.documentFirstHeading').text() || $('title').text());

        if (description.length > 0) {
            text = title + ' - ' + description;
        } else {
            text = $('title').text();
        }

        return text;
    }

    // build URI from rel="canonical" or document.location
    function getURI() {
        var uri = document.location.href;
        var canonical = $("link[rel=canonical]").attr("href");

        if (canonical && canonical.length > 0) {
            if (canonical.indexOf("http") < 0) {
                canonical = document.location.protocol + "//" + document.location.host + canonical;
            }
            uri = canonical;
        }

        return uri;
    }

    function cookieSet(name, value, days, path, domain) {
        var expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = name + '=' + value + '; expires=' + expires.toUTCString() + '; path=' + path + '; domain=' + domain;
    }
    function cookieDel(name, value, path, domain) {
        var expires = new Date();
        expires.setTime(expires.getTime() - 100);
        document.cookie = name + '=' + value + '; expires=' + expires.toUTCString() + '; path=' + path + '; domain=' + domain;
    }

    // extend jquery with our plugin function
    $.fn.socialSharePrivacy = function (settings) {
        var defaults = {
            'services' : {
                'facebook' : {
                    'status'            : 'on',
                    'dummy_img'         : portal_url + '/++resource++xhostplus.social.images/dummy_facebook_en.png',
                    'txt_info'          : '2 clicks for your privacy: Only if you click here the button will get active and you can send your recommendation to Facebook. An active button will send data do a third-party &ndash; more information on <em>i</em>.',
                    'txt_fb_off'        : 'not connected to Facebook',
                    'txt_fb_on'         : 'connected to Facebook',
                    'perma_option'      : 'on',
                    'display_name'      : 'Facebook',
                    'referrer_track'    : '',
                    'language'          : 'en_GB',
                    'action'            : 'like'
                },
                'twitter' : {
                    'status'            : 'on',
                    'dummy_img'         : portal_url + '/++resource++xhostplus.social.images/dummy_twitter_en.png',
                    'txt_info'          : '2 clicks for your privacy: Only if you click here the button will get active and you can send your recommendation to Twitter. An active button will send data do a third-party &ndash; more information on <em>i</em>.',
                    'txt_twitter_off'   : 'not connected to Twitter',
                    'txt_twitter_on'    : 'connected to Twitter',
                    'perma_option'      : 'on',
                    'display_name'      : 'Twitter',
                    'referrer_track'    : '',
                    'tweet_text'        : getTweetText,
                    'short_url'         : '',
                    'hashtags'          : '',
                    'language'          : 'en'
                },
                'gplus' : {
                    'status'            : 'on',
                    'dummy_img'         : portal_url + '/++resource++xhostplus.social.images/dummy_googleplus_en.png',
                    'txt_info'          : '2 clicks for your privacy: Only if you click here the button will get active and you can send your recommendation to Google+. An active button will send data do a third-party &ndash; more information on <em>i</em>.',
                    'txt_gplus_off'     : 'not connected to Google+',
                    'txt_gplus_on'      : 'connected to Google+',
                    'perma_option'      : 'on',
                    'display_name'      : 'Google+',
                    'referrer_track'    : '',
                    'language'          : 'en'
                },
                'linkedin' : {
                    'status'            : 'on',
                    'dummy_img'         : portal_url + '/++resource++xhostplus.social.images/dummy_linkedin_en.png',
                    'txt_info'          : '2 clicks for your privacy: Only if you click here the button will get active and you can send your recommendation to LinkedIn. An active button will send data do a third-party &ndash; more information on <em>i</em>.',
                    'txt_linkedin_off'  : 'not connected to LinkedIn',
                    'txt_linkedin_on'   : 'connected to LinkedIn',
                    'perma_option'      : 'on',
                    'display_name'      : 'LinkedIn',
                    'referrer_track'    : '',
                    'language'          : 'en'
                }
            },
            'info_link'         : 'http://www.heise.de/ct/artikel/2-Klicks-fuer-mehr-Datenschutz-1333879.html',
            'txt_help'          : 'Only if you activate the buttons, data will get sent to Facebook, Twitter, Google or LinkedIn. This data might get stored in the USA. Get more information by clicking on <em>i</em>.',
            'settings_perma'    : 'Activate buttons permanently:',
            'cookie_path'       : portal_url,
            'cookie_domain'     : document.location.host,
            'cookie_expires'    : '365',
            'css_path'          : portal_url + '/++resource++xhostplus.social.stylesheets/socialshareprivacy.css',
            'uri'               : getURI
        };

        // Standardwerte des Plug-Ings mit den vom User angegebenen Optionen ueberschreiben
        var options = $.extend(true, defaults, settings);

        var facebook_on = (options.services.facebook.status === 'on');
        var twitter_on  = (options.services.twitter.status  === 'on');
        var gplus_on    = (options.services.gplus.status    === 'on');
        var linkedin_on = (options.services.linkedin.status === 'on');

        // check if at least one service is "on"
        if (!facebook_on && !twitter_on && !gplus_on && !linkedin_on) {
            return;
        }

        // insert stylesheet into document and prepend target element
        if (options.css_path.length > 0) {
            $('head').append('<link rel="stylesheet" type="text/css" href="' + options.css_path + '" />');
        }
        $(this).prepend('<ul class="social_share_privacy_area"></ul>');
        var context = $('.social_share_privacy_area', this);

        // canonical uri that will be shared
        var uri = options.uri;
        if (typeof uri === 'function') {
            uri = uri();
        }

        return this.each(function () {

            //
            // Facebook
            //
            if (facebook_on) {
                var fb_enc_uri = encodeURIComponent(uri + options.services.facebook.referrer_track);
                var fb_code = '<iframe src="http://www.facebook.com/plugins/like.php?locale=' + options.services.facebook.language + '&amp;href=' + fb_enc_uri + '&amp;send=false&amp;layout=button_count&amp;width=120&amp;show_faces=false&amp;action=' + options.services.facebook.action + '&amp;colorscheme=light&amp;font&amp;height=21" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:145px; height:21px;" allowTransparency="true"></iframe>';
                var fb_dummy_btn = '<img src="' + options.services.facebook.dummy_img + '" alt="Facebook &quot;Like&quot;-Dummy" class="fb_like_privacy_dummy" />';

                context.append('<li class="facebook help_info"><span class="info">' + options.services.facebook.txt_info + '</span><span class="switch off">' + options.services.facebook.txt_fb_off + '</span><div class="fb_like dummy_btn">' + fb_dummy_btn + '</div></li>');

                var $container_fb = $('li.facebook', context);

                $('li.facebook div.fb_like img.fb_like_privacy_dummy,li.facebook span.switch', context).live('click', function () {
                    if ($container_fb.find('span.switch').hasClass('off')) {
                        $container_fb.addClass('info_off');
                        $container_fb.find('span.switch').addClass('on').removeClass('off').html(options.services.facebook.txt_fb_on);
                        $container_fb.find('img.fb_like_privacy_dummy').replaceWith(fb_code);
                    } else {
                        $container_fb.removeClass('info_off');
                        $container_fb.find('span.switch').addClass('off').removeClass('on').html(options.services.facebook.txt_fb_off);
                        $container_fb.find('.fb_like').html(fb_dummy_btn);
                    }
                });
            }

            //
            // Twitter
            //
            if (twitter_on) {
                var text = options.services.twitter.tweet_text;
                if (typeof text === 'function') {
                    text = text();
                }

                var twitter_url = options.services.twitter.short_url;
                if (twitter_url.length == 0) {
                    twitter_url = uri;
                }

                // 140 minus additional chars
                var url_length = (twitter_url + options.services.twitter.referrer_track).length + 2;
                var hashtags = options.services.twitter.hashtags.split(',');
                var hashtags_length = 0;
                for(var i in hashtags) {
                    var tag = hashtags[i];
                    hashtags_length += tag.length + 1;
                }
                hashtags_length += hashtags.length;

                var text_max_length = (140 - url_length - hashtags_length);
                if (text_max_length < 0)
                    text_max_length = 0;
                else if(text_max_length > 120)
                    text_max_length = 120;

                text = abbreviateText(text, text_max_length);

                var text = encodeURIComponent(text);
                var twitter_enc_uri = encodeURIComponent(twitter_url + options.services.twitter.referrer_track);
                var twitter_count_url = encodeURIComponent(uri);
                var twitter_hashtags = encodeURIComponent(options.services.twitter.hashtags);

                var twitter_code = '<iframe allowtransparency="true" frameborder="0" scrolling="no" src="http://platform.twitter.com/widgets/tweet_button.html?url=' + twitter_enc_uri + '&amp;hashtags=' + twitter_hashtags + '&amp;counturl=' + twitter_count_url + '&amp;text=' + text + '&amp;count=horizontal&amp;lang=' + options.services.twitter.language + '" style="width:130px; height:25px;"></iframe>';
                var twitter_dummy_btn = '<img src="' + options.services.twitter.dummy_img + '" alt="&quot;Tweet this&quot;-Dummy" class="tweet_this_dummy" />';

                context.append('<li class="twitter help_info"><span class="info">' + options.services.twitter.txt_info + '</span><span class="switch off">' + options.services.twitter.txt_twitter_off + '</span><div class="tweet dummy_btn">' + twitter_dummy_btn + '</div></li>');

                var $container_tw = $('li.twitter', context);

                $('li.twitter div.tweet img,li.twitter span.switch', context).live('click', function () {
                    if ($container_tw.find('span.switch').hasClass('off')) {
                        $container_tw.addClass('info_off');
                        $container_tw.find('span.switch').addClass('on').removeClass('off').html(options.services.twitter.txt_twitter_on);
                        $container_tw.find('img.tweet_this_dummy').replaceWith(twitter_code);
                    } else {
                        $container_tw.removeClass('info_off');
                        $container_tw.find('span.switch').addClass('off').removeClass('on').html(options.services.twitter.txt_twitter_off);
                        $container_tw.find('.tweet').html(twitter_dummy_btn);
                    }
                });
            }

            //
            // Google+
            //
            if (gplus_on) {
                // fuer G+ wird die URL nicht encoded, da das zu einem Fehler fuehrt
                var gplus_uri = uri + options.services.gplus.referrer_track;

                // we use the Google+ "asynchronous" code, standard code is flaky if inserted into dom after load
                var gplus_code = '<div class="g-plusone" data-size="medium" data-annotation="bubble" data-href="' + gplus_uri + '"></div><script type="text/javascript">window.___gcfg = {lang: "' + options.services.gplus.language + '"}; (function() { var po = document.createElement("script"); po.type = "text/javascript"; po.async = true; po.src = "https://apis.google.com/js/plusone.js"; var s = document.getElementsByTagName("script")[0]; s.parentNode.insertBefore(po, s); })(); </script>';
                var gplus_dummy_btn = '<img src="' + options.services.gplus.dummy_img + '" alt="&quot;Google+1&quot;-Dummy" class="gplus_one_dummy" />';

                context.append('<li class="gplus help_info"><span class="info">' + options.services.gplus.txt_info + '</span><span class="switch off">' + options.services.gplus.txt_gplus_off + '</span><div class="gplusone dummy_btn">' + gplus_dummy_btn + '</div></li>');

                var $container_gplus = $('li.gplus', context);

                $('li.gplus div.gplusone img,li.gplus span.switch', context).live('click', function () {
                    if ($container_gplus.find('span.switch').hasClass('off')) {
                        $container_gplus.addClass('info_off');
                        $container_gplus.find('span.switch').addClass('on').removeClass('off').html(options.services.gplus.txt_gplus_on);
                        $container_gplus.find('img.gplus_one_dummy').replaceWith(gplus_code);
                    } else {
                        $container_gplus.removeClass('info_off');
                        $container_gplus.find('span.switch').addClass('off').removeClass('on').html(options.services.gplus.txt_gplus_off);
                        $container_gplus.find('.gplusone').html(gplus_dummy_btn);
                    }
                });
            }

            //
            // LinkedIn
            //
            if (linkedin_on) {
                var linkedin_enc_uri = encodeURIComponent(uri + options.services.linkedin.referrer_track);

                var linkedin_code = '<script src="//platform.linkedin.com/in.js" type="text/javascript"></script><script type="IN/Share" data-counter="right"></script>';
                var linkedin_dummy_btn = '<img src="' + options.services.linkedin.dummy_img + '" alt="&quot;LinkedIn&quot;-Dummy" class="linkedin_dummy" />';

                context.append('<li class="linkedin help_info"><span class="info">' + options.services.linkedin.txt_info + '</span><span class="switch off">' + options.services.linkedin.txt_linkedin_off + '</span><div class="inshare dummy_btn">' + linkedin_dummy_btn + '</div></li>');

                var $container_linkedin = $('li.linkedin', context);

                $('li.linkedin div.inshare img,li.linkedin span.switch', context).live('click', function () {
                    if ($container_linkedin.find('span.switch').hasClass('off')) {
                        $container_linkedin.addClass('info_off');
                        $container_linkedin.find('span.switch').addClass('on').removeClass('off').html(options.services.linkedin.txt_linkedin_on);
                        $container_linkedin.find('img.linkedin_dummy').replaceWith(linkedin_code);
                    } else {
                        $container_linkedin.removeClass('info_off');
                        $container_linkedin.find('span.switch').addClass('off').removeClass('on').html(options.services.linkedin.txt_linkedin_off);
                        $container_linkedin.find('.inshare').html(linkedin_dummy_btn);
                        window.IN = null;
                    }
                });
            }

            //
            // Der Info/Settings-Bereich wird eingebunden
            //
            context.append('<li class="settings_info"><div class="settings_info_menu off perma_option_off"><a href="' + options.info_link + '"><span class="help_info icon"><span class="info">' + options.txt_help + '</span></span></a></div></li>');

            // Info-Overlays mit leichter Verzoegerung einblenden
            $('.help_info:not(.info_off)', context).live('mouseenter', function () {
                var $info_wrapper = $(this);
                var timeout_id = window.setTimeout(function () { $($info_wrapper).addClass('display'); }, 500);
                $(this).data('timeout_id', timeout_id);
            });
            $('.help_info', context).live('mouseleave', function () {
                var timeout_id = $(this).data('timeout_id');
                window.clearTimeout(timeout_id);
                if ($(this).hasClass('display')) {
                    $(this).removeClass('display');
                }
            });

            var facebook_perma = (options.services.facebook.perma_option === 'on');
            var twitter_perma  = (options.services.twitter.perma_option  === 'on');
            var gplus_perma    = (options.services.gplus.perma_option    === 'on');
            var linkedin_perma = (options.services.linkedin.perma_option === 'on');

            // Menue zum dauerhaften Einblenden der aktiven Dienste via Cookie einbinden
            // Die IE7 wird hier ausgenommen, da er kein JSON kann und die Cookies hier ueber JSON-Struktur abgebildet werden
            if (((facebook_on && facebook_perma)
                || (twitter_on && twitter_perma)
                || (gplus_on && gplus_perma)
                || (linkedin_on && linkedin_perma))
                    && (!$.browser.msie || ($.browser.msie && $.browser.version > 7.0))) {

                // CUSTOM: Anfuerungszeichen vom Wert des Cookies entfernen
                var quote_remove = function(str) {
                    return str.replace(/"+/g, "");
                }

                // Cookies abrufen
                var cookie_list = document.cookie.split(';');
                var cookies = '{';
                var i = 0;
                for (; i < cookie_list.length; i += 1) {
                    var foo = cookie_list[i].split('=');
                    cookies += '"' + $.trim(foo[0]) + '":"' + quote_remove($.trim(foo[1])) + '"';
                    if (i < cookie_list.length - 1) {
                        cookies += ',';
                    }
                }
                cookies += '}';
                cookies = JSON.parse(cookies);

                // Container definieren
                var $container_settings_info = $('li.settings_info', context);

                // Klasse entfernen, die das i-Icon alleine formatiert, da Perma-Optionen eingeblendet werden
                $container_settings_info.find('.settings_info_menu').removeClass('perma_option_off');

                // Perma-Optionen-Icon (.settings) und Formular (noch versteckt) einbinden
                $container_settings_info.find('.settings_info_menu').append('<span class="settings">Settings</span><form><fieldset><legend>' + options.settings_perma + '</legend></fieldset></form>');


                // Die Dienste mit <input> und <label>, sowie checked-Status laut Cookie, schreiben
                var checked = ' checked="checked"';
                if (facebook_on && facebook_perma) {
                    var perma_status_facebook = cookies.socialSharePrivacy_facebook === 'perma_on' ? checked : '';
                    $container_settings_info.find('form fieldset').append(
                        '<input type="checkbox" name="perma_status_facebook" id="perma_status_facebook"'
                            + perma_status_facebook + ' /><label for="perma_status_facebook">'
                            + options.services.facebook.display_name + '</label>'
                    );
                }

                if (twitter_on && twitter_perma) {
                    var perma_status_twitter = cookies.socialSharePrivacy_twitter === 'perma_on' ? checked : '';
                    $container_settings_info.find('form fieldset').append(
                        '<input type="checkbox" name="perma_status_twitter" id="perma_status_twitter"'
                            + perma_status_twitter + ' /><label for="perma_status_twitter">'
                            + options.services.twitter.display_name + '</label>'
                    );
                }

                if (gplus_on && gplus_perma) {
                    var perma_status_gplus = cookies.socialSharePrivacy_gplus === 'perma_on' ? checked : '';
                    $container_settings_info.find('form fieldset').append(
                        '<input type="checkbox" name="perma_status_gplus" id="perma_status_gplus"'
                            + perma_status_gplus + ' /><label for="perma_status_gplus">'
                            + options.services.gplus.display_name + '</label>'
                    );
                }

                if (linkedin_on && linkedin_perma) {
                    var perma_status_linkedin = cookies.socialSharePrivacy_linkedin === 'perma_on' ? checked : '';
                    $container_settings_info.find('form fieldset').append(
                        '<input type="checkbox" name="perma_status_linkedin" id="perma_status_linkedin"'
                            + perma_status_linkedin + ' /><label for="perma_status_linkedin">'
                            + options.services.linkedin.display_name + '</label>'
                    );
                }

                // Cursor auf Pointer setzen fuer das Zahnrad
                $container_settings_info.find('span.settings').css('cursor', 'pointer');

                // Einstellungs-Menue bei mouseover ein-/ausblenden
                $($container_settings_info.find('span.settings'), context).live('mouseenter', function () {
                    var timeout_id = window.setTimeout(function () { $container_settings_info.find('.settings_info_menu').removeClass('off').addClass('on'); }, 500);
                    $(this).data('timeout_id', timeout_id);
                });
                $($container_settings_info, context).live('mouseleave', function () {
                    var timeout_id = $(this).data('timeout_id');
                    window.clearTimeout(timeout_id);
                    $container_settings_info.find('.settings_info_menu').removeClass('on').addClass('off');
                });

                // Klick-Interaktion auf <input> um Dienste dauerhaft ein- oder auszuschalten (Cookie wird gesetzt oder geloescht)
                $($container_settings_info.find('fieldset input')).live('click', function (event) {
                    var click = event.target.id;
                    var service = click.substr(click.lastIndexOf('_') + 1, click.length);
                    var cookie_name = 'socialSharePrivacy_' + service;

                    if ($('#' + event.target.id + ':checked').length) {
                        cookieSet(cookie_name, 'perma_on', options.cookie_expires, options.cookie_path, options.cookie_domain);
                        $('form fieldset label[for=' + click + ']', context).addClass('checked');
                    } else {
                        cookieDel(cookie_name, 'perma_on', options.cookie_path, options.cookie_domain);
                        $('form fieldset label[for=' + click + ']', context).removeClass('checked');
                    }
                });

                // Dienste automatisch einbinden, wenn entsprechendes Cookie vorhanden ist
                if (facebook_on && facebook_perma && cookies.socialSharePrivacy_facebook === 'perma_on') {
                    $('li.facebook span.switch', context).click();
                }
                if (twitter_on && twitter_perma && cookies.socialSharePrivacy_twitter === 'perma_on') {
                    $('li.twitter span.switch', context).click();
                }
                if (gplus_on && gplus_perma && cookies.socialSharePrivacy_gplus === 'perma_on') {
                    $('li.gplus span.switch', context).click();
                }
                if (linkedin_on && linkedin_perma && cookies.socialSharePrivacy_linkedin === 'perma_on') {
                    $('li.linkedin span.switch', context).click();
                }
            }
        }); // this.each(function ()
    };      // $.fn.socialSharePrivacy = function (settings) {
}(jQuery));
