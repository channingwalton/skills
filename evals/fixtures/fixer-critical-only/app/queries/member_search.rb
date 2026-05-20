# frozen_string_literal: true

class MemberSearch
  def call(query)
    Member.where("name ILIKE '%#{query}%'")
  end
end
