test("Test j01Dialog", function() {
    var handler = $("#myDialogHandler");
    handler.j01Dialog({j01DialogExpression: '#myDialog'});
	equals( false, $('#myDialog').is(":visible") );
	handler.click();
	equals( true, $('#myDialog').is(":visible") );
});