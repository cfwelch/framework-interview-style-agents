
$(function() {
	$(".tabs").tabs();
});

function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

$(window).resize(function() {
	var viewportWidth = $(window).width();
	//var viewportHeight = $(window).height();
	if (viewportWidth > 1000) {
		var x = document.getElementById('mySidenav');
		x.style = '';
		var x2 = document.getElementById('container');
		x2.classList = '';
	}
});

function menuButtonToggle(x2) {
	x2.classList.toggle("change");
	var x = document.getElementById('mySidenav');
	//alert(x.style.display)
	if (x.style.display === 'none' || x.style.display.trim() ==='') {
		x.style.display = 'block';
	} else {
		x.style.display = 'none';
	}
}

function pop(div) {
	document.getElementById(div).style.display = 'block';
	document.getElementById("showing").value = div;
}

function hide(div) {
	document.getElementById(div).style.display = 'none';
}

//To detect escape button
document.onkeydown = function(evt) {
	evt = evt || window.event;
	if (evt.keyCode == 27) {
		$("div[id^='popDiv']").each(function(index) {
			hide($(this).attr("id"));
		});
	}
};
