# frozen_string_literal: true

require "minitest/autorun"
require_relative "../app/models/member"
require_relative "../app/queries/member_search"

class MemberSearchTest < Minitest::Test
  def test_uses_bound_parameter_for_query
    MemberSearch.new.call("%') OR 1=1 --")

    assert_equal "name ILIKE ?", Member.last_condition
    assert_equal ["%%') OR 1=1 --%"], Member.last_params
  end
end
