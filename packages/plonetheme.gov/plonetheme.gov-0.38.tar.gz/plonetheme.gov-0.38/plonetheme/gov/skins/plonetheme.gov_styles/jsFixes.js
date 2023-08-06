GovJSFixes = {};

GovJSFixes.fixCaptions = function ()
{
	var leadimage = jq(".newsImageContainer a img");
	var width = leadimage.width();
	if (width >10)
	{
		jq(".newsImageContainer p").css({'max-width' : width});
	}
};

GovJSFixes.carouselFix = function ()
{
	setTimeout(function () {
		$(".carousel").css('visibility', 'visible');
	}, 1000);
}

GovJSFixes.runFixes = function ()
{
	//Add new fixes to this list to activate them
	GovJSFixes.carouselFix();
};


GovJSFixes.runSpecialFixes = function ()
{
	//Add new fixes to this list to activate them and ONLY RUN WHEN THE FULL PAGE IS LOADED
	GovJSFixes.fixCaptions();
};

//run all the fixes when the DOM is completely loaded and the special ones when everything is loaded;
jq(window).load(function () {GovJSFixes.runSpecialFixes();});
jq(document).ready(function () {GovJSFixes.runFixes();}); 
