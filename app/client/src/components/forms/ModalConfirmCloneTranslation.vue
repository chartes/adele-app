<template>
  
  <modal-confirm
      :title="'Cloner la traduction ?'"
      :submitText="'Cloner'"
      :cancel="cancelAction"
      :submit="submitAction"
      class="has-text"
  >
    <p><b class="has-text-info">Attention : vous êtes sur le point de cloner le traduction</b></p>
    <br/>
    <p>Vous copierez ainsi le contenu et les notes liées à la traduction de l'élève.</p>
    <p>Cette opération <b>écrasera votre propre version de la traduction et la remplacera par celle de l'élève.</b></p>
    <p>Votre nouvelle traduction devra être de nouveau <b>validée</b> manuellement.</p>
    <p></p>
  </modal-confirm>

</template>

<script>
	
	import ModalConfirm from './ModalConfirm';
	
	export default {
		name: "modal-confirm-clone-translation",
		props: ['cancel', 'submit'],
		components: {
			ModalConfirm
		},
		methods: {
			submitAction () {
				this.$props.submit(this.selected);
			},
			cancelAction () {
				this.$props.cancel();
			}
		}
	}
</script>
