import { create } from "zustand"

export const useDomainStore = create((set) => ({
  domains: [],
  activeDomainId: null,

  setDomains: (domains) => {
    set({ domains })
  },

  setActive: (id) => {
    set({ activeDomainId: id })
  },
}))