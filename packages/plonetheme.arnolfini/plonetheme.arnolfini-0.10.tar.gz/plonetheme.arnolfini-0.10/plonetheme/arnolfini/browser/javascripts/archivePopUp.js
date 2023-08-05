Arnolfini.archivePopUp = {}

Arnolfini.archivePopUp.activateLinks = function () {
    $('dl.portlet.portlet-archiveportlet .portletItem .yearItem.undocYear a').click(function(event)
                                                                                    {
                                                                                        href = $(event.target).attr('href');
                                                                                        Arnolfini.archivePopUp.showMessage(href);
                                                                                        return false;
                                                                                    });
}

Arnolfini.archivePopUp.showMessage = function (href)
{
    var title = $('<h2 class="archivePopupTitle">'+href+'</h2>')
    var message = "This year only contains undocumented events. It might be that we have no documentation about the events described or we are still in the process of digitalizing the content. Are you sure you want to continue to this year?";
    var popupDiv = $('<div id="archivepopup"></div>');
    var messageDiv = $('<div class="message"></div>');
    var cancelButton = $('<div class="cancelButton">Cancel</div>')
    var continueButton = $('<div class="continueButton">Continue</div>');
    
    $(cancelButton).click(Arnolfini.archivePopUp.closeMessage);
    $(continueButton).click(function () {window.location = href})
    
    $(messageDiv).text(message);
    $(popupDiv).append(title);
    $(popupDiv).append(messageDiv);
    $(popupDiv).append(cancelButton);
    $(popupDiv).append(continueButton);
    $('body').append(popupDiv);
}

Arnolfini.archivePopUp.closeMessage = function ()
{
    $('#archivepopup').remove();
}

$(function ()
{
    Arnolfini.archivePopUp.activateLinks(); 
});