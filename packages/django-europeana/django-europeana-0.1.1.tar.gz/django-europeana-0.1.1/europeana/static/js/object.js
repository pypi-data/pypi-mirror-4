$(document).ready(function() {
	xOffset = 150;
	yOffset = 30;
	
	$("a.europeana-image-link").hover(function(e){
		this.t = this.title;
		
		this.title = "";
		var c = "";
		
		var imageLink = $(this).attr("href");
		$("body").append("<p id='preview'><img src='"+ imageLink +"' alt='Image preview' />"+ c +"</p>");
		$("#preview")
			.css("top",(e.pageY - xOffset) + "px")
			.css("left",(e.pageX + yOffset) + "px")
			.fadeIn(500);					
	    },
		function(){
			this.title = this.t;	
			$("#preview").remove();
	    });	
		$("a.europeana-image-link").mousemove(function(e){
			$("#preview")
				.css("top",(e.pageY - xOffset) + "px")
				.css("left",(e.pageX + yOffset) + "px");
		});
});
