/*!
* Aloha Editor
* Author & Copyright (c) 2010 Gentics Software GmbH
* aloha-sales@gentics.com
* Licensed unter the terms of http://www.aloha-editor.com/license.html
*/

define(
['aloha/jquery', 'aloha/contenthandlermanager', 'block/blockmanager'],
function(jQuery, ContentHandlerManager, BlockManager) {

	/**
	 * @name block.BlockContentHandler
	 * @class Special block content handler
	 *
	 * The blog content handler handles pasting of blocks in editables. Pasted
	 * block markup will be replaced by a newly created block instance.
	 */
	var BlockContentHandler = ContentHandlerManager.createHandler(
	/** @lends block.BlockContentHandler */
	{
		/**
		 * Handle the pasting. Remove all unwanted stuff.
		 *
		 * There are two main cases which we need to distinguish:
		 * 1) Aloha Blocks are selected, and crtl+c is pressed then. In this case, *only the block* is copied / pasted.
		 * 2) Text is selected, but the selection also spans an aloha block.
		 *
		 * Generally, case 2) seems to work without bigger problems in Webkit / Firefox, while
		 * case 1) results in very much undesired and inconsistent behavior. If 1) happens,
		 * the property "data-aloha-block-copy-only-block" is set to "true"; so we can kick in and
		 * do additional cleanups.
		 * @param {jQuery} content
		 */
		handleContent: function( content ) {
			if ( typeof content === 'string' ){
				content = jQuery( '<div>' + content + '</div>' );
			} else if ( content instanceof jQuery ) {
				content = jQuery( '<div>' ).append(content);
			}

			if (content.find('.aloha-block[data-aloha-block-copy-only-block="true"]').length > 0) {
				// We are in case 1; so some more cleanup is needed (at least in webkit and firefox).

				// Webkit seems to *duplicate* the block when copying. The duplicated
				// block has *no ID property* set, that's how we can find and discard it.
				// Very ugly!
				content.find('.aloha-block:not([id])').remove();
				// Further cleanup for Webkit, removing empty nodes. Quite hacky!
				content.find('.aloha-block + span:empty').remove();
				content.find('div:empty').remove();
				// (another) Hack for Webkit, removing superfluous BR
				content.find('br.Apple-interchange-newline').remove();

				// Firefox adds a <br> directly before the .aloha-block...
				content.find('.aloha-block').prev('br').remove();

				// Chrome (at least) sometimes adds an empty <br> inside an (otherwise empty) span
				content.find('div > br:only-child').parent().remove();

			}

			content.find('.aloha-block').each(function() {
				var oldBlock = jQuery(this);

				var elementAttributes = {}; // all attributes except data-*
				var blockAttributes = {}; // all data* attributes
				jQuery.each(oldBlock[0].attributes, function(k, v) {
					if (v.nodeName === 'id') return;

					if (v.nodeName.match(/^data-/)) {
						blockAttributes[v.nodeName.substr(5)] = v.nodeValue;
					} else {
						elementAttributes[v.nodeName] = v.nodeValue;
					}
				});

				var newBlockId = GENTICS.Utils.guid();

				var newBlock = jQuery('<' + this.tagName + '/>')
					.attr(elementAttributes)
					.attr('id', newBlockId)
					.removeClass('aloha-block-active')
					.removeClass('aloha-block')
					.html(oldBlock.html());

				oldBlock.replaceWith(newBlock);

				// We need to blockify the contents with a timeout, as we need the connected DOM node for it.
				window.setTimeout(function() {
					BlockManager._blockify(jQuery('#' + newBlockId), blockAttributes);
				}, 50);
			});

			return content.html();
		}
	});
	return BlockContentHandler;
});
