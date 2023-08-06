(($) ->
	$.sublimeScroll = (options) ->
		# Default settings
		settings =
			scroll_width: 150
			offset: 0
			z_index: 50
			content_width: 960
			full_height: $('html').height()
			opacity: 0.1
			color: 'white'

		# Merge default settings with options.
		settings = $.extend settings, options

		# Actual Script:
		window_height = null
		scroll_height = null
		scroll_bar_height = null

		size_factor = (settings.scroll_width / settings.content_width)

		scroll_offset = settings.offset * size_factor

		$scroll = $ '<div>',
			id: 'sublime-scroll'
		.css
			position: 'fixed'
			top: settings.offset
			right: 0
			width: settings.scroll_width
			zIndex:settings.z_index
			backgroundRepeat: 'no-repeat'
			backgroundPosition: "0 " + (scroll_offset * -1) + 'px'
		.appendTo($('body'))

		$scroll_bar = $ '<div>',
			id: 'sublime-scroll-bar'
		.css
			position: 'absolute'
			right: 0
			width: '100%'
			backgroundColor: settings.color
			opacity: settings.opacity
			zIndex:settings.z_index + 1
		.appendTo($scroll)

		$scroll_overlay = $ '<div>',
			id: 'sublime-scroll-overlay'
		.css
			position: 'fixed'
			top: settings.offset
			right: 0
			width: settings.scroll_width
			height:'100%'
			zIndex:settings.z_index + 2
		.appendTo($scroll)

		onDragEnd = (event) ->
			event.preventDefault()
			$scroll_overlay.css({width:settings.scroll_width})
			$(window).off('mousemove', onDrag)

		onDrag = (event) ->
			if not (event.target is $scroll_overlay[0])
				return false

			y = event.offsetY - scroll_bar_height / 2

			max_pos = scroll_height - scroll_bar_height - scroll_offset

			if y < 0
				y = 0
			if y > max_pos
				y = max_pos

			$scroll_bar.css
				top: y

			pos = y / size_factor + scroll_offset

			$(window).scrollTop(pos)

		$scroll.on 'mousedown', (event) ->
			event.preventDefault()

			$scroll_overlay.css({width:'100%'})

			$(window).on('mousemove', onDrag).one('mouseup', onDragEnd)
			onDrag(event)

		$(window).resize ->
			window_height = $(window).height() - settings.offset

			scroll_height = settings.full_height * size_factor - scroll_offset
			#console.log settings.full_height, scroll_height
			if scroll_height < window_height
				height = window_height
			else
				height = scroll_height

			$scroll.css
				height: height
				backgroundSize: "100% " + scroll_height + "px"

			$scroll_overlay.css
				height: height

			scroll_bar_height = window_height * size_factor

			$scroll_bar.css
				height: scroll_bar_height

			$(window).scroll()
		.resize()

		$(window).scroll ->
			scroll_top = $(window).scrollTop()
			pos = (scroll_top + settings.offset) * size_factor - scroll_offset
			$scroll_bar.css({top: pos})

			if scroll_height > window_height
				y = $scroll_bar.position().top
				
				f = (scroll_bar_height / scroll_height) * y

				#console.log scroll_bar_height, scroll_height, (scroll_bar_height / scroll_height), y, f

				margin = (y / scroll_height) * (window_height - scroll_height) - f
			else
				margin = 0

			$scroll.css
				marginTop: margin

			$scroll_overlay.css
				marginTop: margin
		.scroll()
)(jQuery)




