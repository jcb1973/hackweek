"use strict";

window.onload = function() {

    var sp = getSpotifyApi();
    var models = sp.require('$api/models');
    var views = sp.require('$api/views');

	var button = document.getElementById("simplify_button");
	button.addEventListener ("click", getAlbums, false);

	var wikiLoaded = false;
	var spotifyLoaded = false;
	var results;
	var artistName;
	var wikiListing;
              
function getAlbums() {

	cleanAlbums();

	var xmlHttp = null;
    wikiListing = null;
    artistName = document.getElementById("artist_name").value;
    searchAlbumsforArtist(artistName);
    var Url = "http://galicjaroadmaraton.pl/myapp?name="+artistName;
    
    xmlHttp = new XMLHttpRequest(); 
    xmlHttp.onreadystatechange=function() {
  		if (xmlHttp.readyState==4 && xmlHttp.status==200) {
  			wikiListing = xmlHttp.responseText;
  			wikiLoaded = true;
  			commonCallback();
    	}
  	}
    xmlHttp.open("GET", Url, true);
    xmlHttp.send();
}

function commonCallback() {
  if (spotifyLoaded && wikiLoaded) {
    renderAlbums(artistName, wikiListing, results);
  }
}

function searchAlbumsforArtist(artist) {
	results = null;
	var search = new models.Search("artist:"+artist);//AND (album:\"Queen\"OR\"Queen II\"OR\"Sheer Heart Attack\"OR\"A Night at the Opera\"OR\"A Day at the Races\"OR\"News of the World\"OR\"Jazz\"OR\"The Game\"OR\"Flash Gordon\"OR\"Hot Space\"OR\"The Works\"OR\"A Kind of Magic\"OR\"The Miracle\"OR\"Innuendo\"OR\"Made in Heaven\"");

	search.localResults = models.LOCALSEARCHRESULTS.APPEND;
	search.searchArtists = false;
	search.searchTracks = false;
	search.searchPlaylists = false;
	search.pageSize = 250;

	search.observe(models.EVENT.CHANGE, function() {
		results = search.albums;
		console.log (search.totalAlbums);
		spotifyLoaded = true;
		commonCallback();
	});
	search.appendNext();
}

function cleanAlbums() {
	var element = document.getElementById('search_results');
  	while (element.firstChild) {
  		element.removeChild(element.firstChild);
	}
}

function possibleMatch(strA, strB) {

	var tempA, tempB, temp= document.createElement('p');
	temp.innerHTML= strA;
	tempA = temp.textContent || temp.innerText;
	temp.innerHTML= strB;
	tempB = temp.textContent || temp.innerText;
	temp=null; 
	
	strA = strA.replace(/\./g,'');
	strB = strB.replace(/\./g,'');
	if (strA.localeCompare(strB) == 0) {
		console.log("slightly clever match: " + strA + " with " + strB);
		return true;
	}
	
	strA = strA.replace(/\b\w{1,3}\b/g,'');
	strB = strB.replace(/\b\w{1,3}\b/g,'');
	if (strA.localeCompare(strB) == 0) {	
		console.log("very clever match: " + strA + " with " + strB);
		return true;
	}
		
	strA = strA.replace(/\W/g,'');
	strB = strB.replace(/\W/g,'');
	if (strA.localeCompare(strB) == 0) {
		console.log("clever match: " + strA + " with " + strB);
		return true;
	}
	
	if (tempA.localeCompare(tempB) == 0) {
		console.log("match that deals with html entities: " + tempA + " with " + tempB);
		return true;
	}
	return false;  
}

function probableMatch(strA, strB) {
	
	strA = strA.toUpperCase();
	strB = strB.toUpperCase();
	if (strA.localeCompare(strB) == 0) {
		console.log("simple match: " + strA + " with " + strB);
		return true;
	}	
	//console.log("NO PROBABLE MATCH  with " + strA + " with " + strB);
	return false;
}

function renderAlbums(artist, albums, results) {
	
	var uri;
	var theAlbums = JSON.parse(albums);
	var searchHTML = document.getElementById('search_results');
	var fragment = document.createDocumentFragment();

	var names = [];
	for (var j=0; j<results.length; j++) {
		console.log("j is " +j+ "  " + results[j].name);
		names[j] = results[j].name;
		names[j] = names[j].toUpperCase();
		names[j] = names[j].replace(/\s/g, '');
		
}
	
	for (var i in theAlbums) {
		
		uri = "";
	
		var title = theAlbums[i].title
		var matched = false;
		var ttitle = title.replace(/\s/g, '');
		if(names.indexOf( ttitle.toUpperCase() ) > -1) {
			console.log("quick match: " + title + " with " + results[names.indexOf( ttitle.toUpperCase() )].name);
			uri = results[names.indexOf( ttitle.toUpperCase() )].uri;
			matched = true;
		}
		
		if (!matched) {
			for (var j=0; j<results.length; j++) {		
				
				if (results[j].playable && probableMatch(title, results[j].name)) {
					uri = results[j].uri;
					year = results[j].year;
					break;
				} 
			}	
		}			
		if (!matched) {
			for (var j=0; j<results.length; j++) {		
				if (results[j].playable && possibleMatch(title, results[j].name)) {
					uri = results[j].uri;
					matched = true;
					break;
				} 
			}
		}
		if (!matched) { console.log("no match for " + title); }
  		var link = document.createElement('li');
  		if (matched) {
        	var a = document.createElement('a');
        	a.href = uri;
        	link.appendChild(a);
        	a.innerHTML = title;
        } else {
            var a = document.createElement('a');
        	a.href = "spotify:search:album:\""+ title + "\" artist:" + artist;
        	link.appendChild(a);
        	a.innerHTML = title + (" (?) ");
        }
    	fragment.appendChild(link);
    	
	}
	 searchHTML.appendChild(fragment);


}
    
function htmlEscape(str) {
        return String(str)
                .replace(/&/g, '&amp;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
    }

function tabs() {
        var args = models.application.arguments;
        if (args) {
            var lastArg = args[args.length - 1];
            if (lastArg !== 'index' && lastArg !== 'tabs') {
                return;
           }
       }

        // compose file
        var file = args.length == 1 ? (args[0] + '.html') : '/tutorials/' + args.slice(0, args.length-1).join('/') + '.html';
        var xhr = new XMLHttpRequest();
        xhr.open('GET', file);
        xhr.onreadystatechange = function () {
            if (xhr.readyState != 4 || xhr.status != 200) return;

            var wrapper = document.getElementById('wrapper');
            wrapper.innerHTML = args[0] === 'index' ? '' : '<ul class="breadcrumb"><li><a href="spotify:app:api-tutorial:index">&laquo; Back to main page</a></li></ul>';
            wrapper.innerHTML += xhr.responseText;

            window.scrollTo(0, 0);
            var htmlSnippets = wrapper.querySelectorAll(".html-snippet");
            for (i = 0; i < htmlSnippets.length; i++) {
                container = htmlSnippets[i].getAttribute("data-container");
                if (container) {
                    document.getElementById(container).innerHTML = '<pre><code data-language="html">' + htmlEscape(htmlSnippets[i].innerHTML) + '</code></pre>';
                }
            }

            // search js snippets
            var scripts = wrapper.querySelectorAll("script");
            for (var i = 0; i < scripts.length; i++) {
                if (scripts[i].getAttribute('type') == 'script/snippet') {
                    var dataExecute = scripts[i].getAttribute('data-execute');
                    if (!dataExecute || dataExecute != 'no') {
                        eval(scripts[i].innerHTML);
                    }
                    var container = scripts[i].getAttribute("data-container");
                    if (container) {
                        document.getElementById(container).innerHTML = '<pre><code data-language="javascript">' + htmlEscape(scripts[i].innerHTML) + '</code></pre>';
                    }
                }
            }

            // search html snippets
            Rainbow.color();
        };
        xhr.send(null);
    }

    models.application.observe(models.EVENT.ARGUMENTSCHANGED, tabs);
};
