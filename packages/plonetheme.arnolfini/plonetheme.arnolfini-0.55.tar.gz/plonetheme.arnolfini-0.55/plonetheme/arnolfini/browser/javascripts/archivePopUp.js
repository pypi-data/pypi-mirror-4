Arnolfini.archivePopUp = {}

Arnolfini.archivePopUp.activateLinks = function () {
    $('.portletItem .yearItem.undocYear a').click(function(event)
                                                                                    {
                                                                                        href = $(event.target).attr('href');
                                                                                        Arnolfini.archivePopUp.showMessage(href);
                                                                                        return false;
                                                                                    });
}

Arnolfini.archivePopUp.showMessage = function (href)
{
    var title = $('<h2 class="archivePopupTitle">'+href.substr(-4)+'</h2>')
    var message = "This year only contains undocumented events. Documentation is either not available or it is in the process of being digitised. Are you sure you want to continue to this year?";
    var popupDiv = $('<div class="archivepopup"></div>');
    var messageDiv = $('<div class="message"></div>');
    var cancelButton = $('<div class="cancelButton">Cancel</div>')
    var continueButton = $('<div class="continueButton">Continue</div>');
    
    $(cancelButton).click(Arnolfini.archivePopUp.closeMessage);
    $(continueButton).click(function () {window.location = href + '?showall=true'})
    
    $(messageDiv).text(message);
    $(popupDiv).append(title);
    $(popupDiv).append(messageDiv);
    $(popupDiv).append(cancelButton);
    $(popupDiv).append(continueButton);
    $('body').append(popupDiv);
}

Arnolfini.archivePopUp.closeMessage = function ()
{
    $('.archivepopup').remove();
}

$(function ()
{
    Arnolfini.archivePopUp.activateLinks(); 
});