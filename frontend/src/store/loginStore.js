import { defineStore } from 'pinia'

export const useLoginStore = defineStore('loginDetails', {
  state: () => ({
    ez_id: null,
    role: null,
  }),

  actions: {
    setLoginDetails(details) {
      this.ez_id = details.ez_id
      this.role = details.role
      console.log(details)
      console.log('set details: ', this.ez_id, this.role)
    },

    clearLoginDetails() {
      this.ez_id = null
      this.role = null
    },
  },
  persist: true,
})
