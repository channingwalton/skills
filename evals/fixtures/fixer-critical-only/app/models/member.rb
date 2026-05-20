# frozen_string_literal: true

class Member
  class << self
    attr_reader :last_condition, :last_params

    # Runs a search query
    def where(condition, *params)
      @last_condition = condition
      @last_params = params
      []
    end
  end
end
