<script>
	export let name;
	import {onMount} from "svelte";

	let messageInput;
	let messages = [];
	let inputText = "";

	onMount(() => {
		messageInput.focus()
	});
	const ws = new WebSocket("ws://localhost:8765");

	ws.onopen = function() {
		messages = [...messages, 'Bem-vindo à sala de chat!'];
	};

	ws.onmessage = function(e) {
		messages = [...messages, 'Recebido: ' + e.data];
	};

	function handleClick(e) {
		if(e.preventDefault) e.preventDefault();
		messages = [...messages, 'Enviado: ' + inputText];
		ws.send(inputText);
		inputText = "";
	};
</script>

<main>
	<h1>{name}</h1>
	<div class="chatbox">
		{#each messages as message}
			<p>{message}</p>
		{/each}
	</div>
	<form class="inputbox">
		<input type="text" bind:this={messageInput} bind:value={inputText}>
		<button type="submit" on:click={handleClick}>Send</button>
	</form>
</main>

<style>
	* {
		box-sizing: border-box;
	}

	main {
		width: calc(100% - 30px);
		text-align: center;
		padding: 1em;
		max-width: 1240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	.chatbox {
		width: 100%;
		height: 50vh;
		padding: 0 1em;
		text-align: left;
		background-color: #eee;
		overflow-y: scroll;
		overscroll-behavior-y: contain;
		scroll-snap-type: y proximity;
	}

	.chatbox p {
		margin-top: 0.5em;
		margin-bottom: 0;
		padding-bottom: 0.5em;
	}

	.chatbox > p:last-child {
		scroll-snap-align: end;
	}

	.inputbox {
		display: flex;
		margin-top: 0.5em;
	}

	.inputbox input {
		flex-grow: 1;
	}
</style>