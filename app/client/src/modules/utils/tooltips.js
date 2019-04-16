

function initTooltips() {
	/* style notes tooltip */
	console.warn("init tooltips", document.getElementsByClassName("note-placeholder"));
	for (const notePlaceHolder of document.getElementsByClassName("note-placeholder")) {
		const noteId = notePlaceHolder.dataset.noteId;
		console.warn("tool tip note", noteId);
		const noteContent = document.querySelector(".note-content[data-note-id='" + noteId + "']");
		tippy(notePlaceHolder, {
			content: noteContent.textContent,
			arrow: true,
			arrowType: 'round',
			size: 'large',
			duration: 200,
			animation: 'scale',
			allowHTML: true,
			theme: 'dark',
			placement: 'right'
		});
		
	}
}

export default initTooltips;
